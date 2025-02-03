from django import forms
from django.contrib.auth.models import User
from . import models
from student.models import CustomUser
from exam import models as QMODEL
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.core.validators import MinLengthValidator
from django.contrib.auth.forms import UserCreationForm
# usercreation forms
class TeacherUserForm(UserCreationForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = CustomUser
        fields = ["first_name","last_name","email","is_staff","id_no","sex","departement"]
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
        fields = ["email", "password", "first_name", "last_name","is_active", "is_staff","departement","sex"]


class StudentSearchForm(forms.Form):
    search_term = forms.CharField(
        max_length=100, 
        required=False, 
        label="",
        widget=forms.TextInput(attrs={'class':'form-control','placeholder': 'first name, last name, id no'})
    )


class CustomUserForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, required=False, label='New Password')
    password2 = forms.CharField(widget=forms.PasswordInput, required=False, label='Confirm New Password')

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'id_no', 'sex', 'departement']
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        # If the password fields are not empty, check if they match
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data

    def save(self, commit=True):
        # Get the instance of the CustomUser
        user = super().save(commit=False)
        
        # If a new password is provided, set it
        if self.cleaned_data.get('password1'):
            user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user
