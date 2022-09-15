from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from UniversityKnowledgeHub.settings import UNIVERSITY_MX_FQDN


class MyUser(AbstractUser):
    credits = models.IntegerField(blank=False, null=False, default=10)
    email = models.EmailField(
        validators=[RegexValidator(rf'^\w+@{UNIVERSITY_MX_FQDN}$', f'Enter a valid @{UNIVERSITY_MX_FQDN} address')],
        blank=False, null=False, default='err@err.err', unique=True)    # session_state = models.CharField(max_length=500, null=True)
    username = models.CharField(max_length=100, null=True)
    latest_sid = models.CharField(max_length=100, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
