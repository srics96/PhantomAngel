from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone

from datetime import datetime

import pytz

tz = pytz.timezone('Asia/Calcutta')


class Role(models.Model):
    
    WEB_FRONT_DEVELOPER = "WFD"
    BACKEND_DEVELOPER = "BD"
    ANDROID_DEVELOPER = "AD"
    iOS_DEVELOPER = "ID"
    DESIGNER = "DS"

    ROLE_CHOICES = (
        (WEB_FRONT_DEVELOPER, "WebFrontendDeveloper"),
        (BACKEND_DEVELOPER, "BackendDeveloper"),
        (ANDROID_DEVELOPER, "AndroidDeveloper"),
        (iOS_DEVELOPER, "iOSDeveloper"),
        (DESIGNER, "Designer"),
    )

    role_name = models.CharField(choices=ROLE_CHOICES, max_length=3, default=ANDROID_DEVELOPER, unique=True)
    
    def __str__(self):
        return self.role_name


class Priority(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    magnitude = models.IntegerField()


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    priority = models.ManyToManyField(Priority)
    
    def __str__(self):
        return self.user.email  


class Manager(models.Model):
    employee_instance = models.OneToOneField(Employee)


class Selection(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    employees = models.ManyToManyField(Employee)


class Project(models.Model):
    project_name = models.CharField(max_length=100, default=None, unique=True)
    start_date = models.DateField(default=datetime.now(tz=tz).date())
    end_date = models.DateField(default=None, null=True)
    manager = models.ForeignKey(Manager)
    employees = models.ManyToManyField(Employee)
    selections = models.ManyToManyField(Selection)  
    
    def __str__(self):
        return self.project_name


class Link(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    link_name = models.CharField(max_length=20)
    url = models.URLField(max_length=200)

    def __str__(self):
        return self.link_name


class Task(models.Model):
    task_name = models.CharField(max_length=100, default=None)
    start_date = models.DateField(default=datetime.now(tz=tz).date())
    deadline = models.DateField(default=None, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    employees = models.ManyToManyField(Employee)

    def __str__(self):
        return self.task_name


class Session(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date_time = models.DateTimeField(default=datetime.now())
    end_date_time = models.DateTimeField(default=None, null=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, default=None)
    
    def __str__(self):
        return self.user.email

    
class Absence(models.Model):

    WORK_FROM_HOME = "WFH"
    LEAVE = "LV"

    ABSENCE_TYPES = (
        (WORK_FROM_HOME, "Work from home"),
        (LEAVE, "Take a leave"),
    )


    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date_time = models.DateTimeField(default=None)
    end_date_time = models.DateTimeField(default=None)
    absence_type = models.CharField(choices=ABSENCE_TYPES, max_length=3, default=LEAVE)

    
    def __str__(self):
        return self.user.email








    
    
    



