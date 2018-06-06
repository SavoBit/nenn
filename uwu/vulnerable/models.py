from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


class Employee(models.Model):
    # so later you'd access employee info like this:
    # u = User.objects.get(foo)
    # u.employee.dob  # this makes another db query FYI
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ssn_regex = RegexValidator(
        regex=r'^\d{3}-\d{2}-\d{4}$',
        message='SSN must be in the format 999-99-9999')
    ssn = models.CharField(max_length=11, validators=[ssn_regex])
    dob = models.DateField()
    # there's a number of problems with validating/storing phone numbers like this,
    # but they're functional so we don't care
    phone_regex = RegexValidator(
        regex=r'^\+?\d?\d{9}$',
        message='Phone number must be in the format +19999999999')
    phone = models.CharField(max_length=12, validators=[phone_regex])


class Workday(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()


class Secret(models.Model):
    '''"Secret" data for Employees'''
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    created = models.DateTimeField()
    value = models.CharField(max_length=256)
