import uuid

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from storages.backends.s3boto3 import S3Boto3Storage
from authentication.models import MyUser

types = [('Chapter', 'Chapter'), ('Code', 'Code'), ('Drop Quiz', 'Drop Quiz'), ('Essay', 'Essay'), ('Exam', 'Exam'),
         ('Exam 1', 'Exam 1'), ('Exam 2', 'Exam 2'), ('Final', 'Final'), ('Homework', 'Homework'), ('Lab', 'Lab'),
         ('Lecture', 'Lecture'), ('Midterm', 'Midterm'), ('Notes', 'Notes'), ('Other', 'Other'), ('Paper', 'Paper'),
         ('Problems', 'Problems'), ('Project', 'Project'), ('Questions', 'Questions'), ('Report', 'Report'),
         ('Syllabus', 'Syllabus'), ('Tutorial', 'Tutorial'), ('Useful File', 'Useful File')]


class PrivateMediaStorage(S3Boto3Storage):
    location = 'private'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False


class Professor(models.Model):
    full_name = models.CharField(max_length=100, null=False)
    email = models.EmailField(max_length=100, null=False)


class Course(models.Model):
    letter_code = models.CharField(max_length=5, null=False)
    number = models.CharField(max_length=8, null=False)
    title = models.CharField(max_length=255, null=True, blank=False)

    def __str__(self):
        return self.letter_code + self.number


class Previous(models.Model):
    description = models.CharField(max_length=500)
    course = models.ForeignKey(to=Course, null=True, blank=True, on_delete=models.DO_NOTHING)
    professor = models.ForeignKey(to=Professor, null=True, blank=True, on_delete=models.DO_NOTHING)
    submitter = models.ForeignKey(to=MyUser, null=True, on_delete=models.DO_NOTHING)
    file = models.FileField()
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=100, choices=types)
    semester = models.CharField(max_length=10, choices=[('Fall', 'Fall'), ('Spring', 'Spring'), ('Summer', 'Summer'),
                                                        ('Winter', 'Winter')])
    academic_year = models.IntegerField()


class Counter4Course(models.Model):
    prev_count = models.IntegerField(null=False, default=0)
    course = models.OneToOneField(to=Course, on_delete=models.CASCADE, null=True, blank=False)


class Counter4User(models.Model):
    prev_count = models.IntegerField(null=False, default=0)
    user = models.OneToOneField(to=MyUser, on_delete=models.CASCADE, null=True, blank=False)


@receiver(post_save, sender=MyUser)
def create_counter4user(sender, instance, **kwargs):
    Counter4User.objects.create(user=instance)


@receiver(post_save, sender=Course)
def create_counter4user(sender, instance, **kwargs):
    Counter4Course.objects.create(course=instance)
