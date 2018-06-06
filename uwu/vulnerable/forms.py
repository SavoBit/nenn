from django.forms import ModelForm
from uwu.vulnerable import models


class EmployeeForm(ModelForm):
    class Meta:
        model = models.Employee
