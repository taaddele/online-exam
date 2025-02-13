from django import forms
from django.contrib.auth.models import User
from . import models
from .models import CustomUser
from exam import models as QMODEL
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.core.validators import MinLengthValidator
from django.contrib.auth.forms import UserCreationForm
# usercreation forms
class StudentUserForm(UserCreationForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    DEPARTMENT_CHOICES = [
        ('computer science', 'Computer Science'),
        ('information technology', 'Information Technology'),
        
        ('software engineering', 'Software Engineering'),
        ('information system', 'Information System'),
        ('civil engineering', 'Civil Engineering'),
        ('mechanical engineering', 'Mechanical Engineering'),
        ('hydraulics engineering', 'Hydraulics Engineering'),
        ('social science', 'Social Science'),
        ('natural science', 'Natural Science'),
        ('health science', 'Health Science'),

        # Add more as needed
    ]

    departement = forms.ChoiceField(choices=DEPARTMENT_CHOICES, widget=forms.Select())
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = CustomUser
        fields = ["first_name","last_name","email","id_no","sex","departement"]

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
       
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords did't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(UserCreationForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ["email", "password", "first_name","id_no", "last_name","is_active", "is_staff","departement","sex"]




