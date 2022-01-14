from django.contrib import admin
from django.urls import path

from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [
      path('', views.loginUser, name="login"),
      path('register/', views.register, name="register"),
      path('verify/<auth_token>', views.verify, name="verify"),
      path('logout/', views.logoutUser, name="logout"),

      path('home/', views.home, name="home"),

      path('reset_password/', auth_views.PasswordResetView.as_view(template_name="User/restPassword/restPassword.html"), name="reset_password"),
      path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="User/restPassword/passwordRestSend.html"),
            name="password_reset_done"),
      path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="User/restPassword/newPssword.html"),
            name="password_reset_confirm"),
      path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="User/restPassword/passwordResetComplete.html"),
            name="password_reset_complete"),


      path('create_link_token/', views.create_link_token, name="create_link_token"),
      path('exchange_public_token/<int:id>/<str:name>/', views.exchange_public_token, name="exchange_public_token"),

      path('get_identity/<int:id>/', views.get_identity, name="get_identity"),
      path('get_transactions/<int:id>/', views.get_transactions, name="get_transactions"),
]
