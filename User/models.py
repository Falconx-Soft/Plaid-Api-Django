from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class accountsCheck(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    crated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class api(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bankName = models.CharField(max_length=200,blank=True,null=True)
    api = models.CharField(max_length=200)

    def __str__(self):
        return self.user.username