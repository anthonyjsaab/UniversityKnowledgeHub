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


class SSOut(models.Model):
    """
    Single Sign OUT designed to be invoked by Microsoft when user signs out from Microsoft's site.
    This is necessary. I cannot simply logout(request) because the request ordered by Microsoft would be received
    as coming from AnonymousUser.
    (Refused to display 'https://e93f9cubheicgvfwugvobwqcf.herokuapp.com/' in a frame because it set 'X-Frame-Options'
    to 'deny'.)
    """
    microsoft_sessionid = models.CharField(max_length=120, null=False)
    django_session = models.ForeignKey(to=Session, on_delete=models.CASCADE)
    user = models.ForeignKey(to=MyUser, on_delete=models.CASCADE)
