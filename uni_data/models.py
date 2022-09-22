from django.db import models
from authentication.models import MyUser


class Professor(models.Model):
    full_name = models.CharField(max_length=100, null=False)
    email = models.EmailField(max_length=100, null=False)


class Course(models.Model):
    letter_code = models.CharField(max_length=5, null=False)
    number = models.CharField(max_length=8, null=False)


class Previous(models.Model):
    s3_object_name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    course = models.ForeignKey(to=Course, null=True, blank=True, on_delete=models.DO_NOTHING)
    professor = models.ForeignKey(to=Professor, null=True, blank=True, on_delete=models.DO_NOTHING)
    submitter = models.ForeignKey(to=MyUser, null=True, on_delete=models.DO_NOTHING)
