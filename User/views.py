import http
from http.client import HTTPResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CutomUserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
import uuid
from django.conf import settings
from django.core.mail import send_mail
from .models import accountsCheck, api

from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.auth_get_request import AuthGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.identity_get_request import IdentityGetRequest
import plaid
from plaid.api import plaid_api
import time
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from datetime import timedelta

# Create your views here.

access_token_hold = ""
configuration = plaid.Configuration(
host=plaid.Environment.Sandbox,
api_key={
	'clientId': '61ddf5292f3735001b80f65c',
	'secret': 'cb37689e78a854f0aa0507325f1c9a',
}
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)


@login_required(login_url='login')
def home(request):
	apiObj = api.objects.filter(user=request.user)
	context = {
		'api':apiObj
	}
	return render(request,'User/home.html',context)

def loginUser(request):

	if request.user.is_authenticated:
		return redirect('home')
	msg = None
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		try:
			user = User.objects.get(username=username)
			user = authenticate(request, username=username, password=password) # check password

			if user is not None and accountsCheck.objects.get(user=user).is_verified:
				login(request, user)
				return redirect('home')
			else:
				msg = 'Password is wrong'
		except:
			msg = 'User not recognized or verified'
	context = {
		'msg':msg
	}
	return render(request,'User/login.html',context)

def register(request):
	msg = None
	form = CutomUserCreationForm
	if request.method == 'POST':
		form = CutomUserCreationForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			# user.username = user.username.lower()
			user.save()
			
			auth_token = str(uuid.uuid4())
			accountsCheck_obj = accountsCheck.objects.create(user=user, auth_token = auth_token)
			accountsCheck_obj.save()

			verificationMain(user.email,auth_token)

			msg = 'We have send a emial varification link to your email kindly visit that link.'
			
			context = {'form':form, 'msg':msg}
			return render(request,'User/register.html', context)
	context = {'form':form, 'msg':msg}
	return render(request,'User/register.html', context)

def verify(request, auth_token):
	accountsCheck_obj = accountsCheck.objects.get(auth_token = auth_token)
	if accountsCheck:
		accountsCheck_obj.is_verified = True
		accountsCheck_obj.save()
		return redirect('login')

def verificationMain(email, auth_token):
	subject = 'Please verify your account'
	message = f'Hi please click on the link to verify your account http://localhost:8000/verify/{auth_token}'
	email_from = settings.EMAIL_HOST_USER
	recipient_list = [email]
	send_mail(subject,message,email_from, recipient_list)

def logoutUser(request):
	logout(request)
	return redirect('login')

@login_required(login_url='login')
def create_link_token(request):
	# Get the client_user_id by searching for the current user
	try:
		request = LinkTokenCreateRequest(
		products=[Products("auth")],
		client_name="Plaid Test App",
		country_codes=[CountryCode('US')],
		# redirect_uri='main.html',
		language='en',
		webhook='https://webhook.example.com',
		user=LinkTokenCreateRequestUser(
			client_user_id='61ddf5292f3735001b80f65c'
			)
		)
		response = client.link_token_create(request)
		key = str(response.link_token)
		r = {
			'key':key
		}
		return JsonResponse({'state':key})
	except plaid.ApiException as e:
		return JsonResponse(e)

@csrf_exempt
def exchange_public_token(request,id,name):
	public_token = request.POST.get('public_token')
	request = ItemPublicTokenExchangeRequest(
        public_token=public_token
     )
	response = client.item_public_token_exchange(request)
	access_token_hold = response['access_token']
	person = User.objects.get(id=id)
	objApi = api(user=person, bankName=name, api = response['access_token'])
	objApi.save()
	print(access_token_hold)
	item_id = response['item_id']
	return JsonResponse(response.to_dict())

@login_required(login_url='login')
def get_auth(request):
    try:
       request = AuthGetRequest(
            access_token=access_token_hold
        )
       response = client.auth_get(request)
       return JsonResponse(response.to_dict())
    except plaid.ApiException as e:
        return JsonResponse(e)

@login_required(login_url='login')
def get_transactions(request, id):
	# Pull transactions for the last 30 days
	start_date = (datetime.now() - timedelta(days=30))
	end_date = datetime.now()
	try:
		token = api.objects.get(id=id)
		options = TransactionsGetRequestOptions()
		request2 = TransactionsGetRequest(
			access_token=token.api,
			start_date=start_date.date(),
			end_date=end_date.date(),
			options=options
		)
		response = client.transactions_get(request2)
		transactions = response.to_dict()['accounts']
		
		context = {'transactions':transactions, 'id':id}
		return render(request, 'User/get_transactions.html', context)
	except plaid.ApiException as e:
		print(e)
		return JsonResponse(e, safe=False)

@login_required(login_url='login')
def get_identity(request, id):
	try:
		token = api.objects.get(id=id)
		request2 = IdentityGetRequest(
			access_token=token.api
		)
		response = client.identity_get(request2)
		value = response.to_dict()['accounts']	
		identity = value
		context = {'identity': identity, 'id':id}
		return render(request, 'User/get_identity.html', context)
	except plaid.ApiException as e:
		print(e)
		return JsonResponse(e, safe=False)