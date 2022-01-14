from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

class CutomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

        def __init__(self, *args, **kwargs):
            super(CutomUserCreationForm, self).__init__(*args, **kwargs)

            for name, fields in self.fields.items():
                fields.widget.attrs.update({'class': 'input'})
