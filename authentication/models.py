from django.contrib.auth.models import AbstractUser
from django.contrib.sessions.models import Session
from django.db import models
from authentication.validators import FQDNValidator


class MyUser(AbstractUser):
    # Used to limit downloads
    credits = models.IntegerField(blank=False, null=False, default=10)
    email = models.EmailField(
        # Helpful when we want to restrict FQDNs
        validators=[FQDNValidator],
        unique=True)
    username = models.CharField(max_length=100, null=False, blank=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class SSOut(models.Model):
    microsoft_sessionid = models.CharField(max_length=120, null=False)
    django_session = models.ForeignKey(to=Session, on_delete=models.CASCADE)
    user = models.ForeignKey(to=MyUser, on_delete=models.CASCADE)
