from django import forms
from .models import Question, Course
from django.core.exceptions import ValidationError
# question forms 
class QuestionForm(forms.ModelForm):
    
    #this will show dropdown __str__ method course model is shown on html so override it
    #to_field_name this will fetch corresponding value  user_id present in course model and return it
    
    class Meta:
        model=Question
        fields=['course','marks','question','option1','option2','option3','option4','answer']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
            'course': forms.Select(attrs={'class': 'form-control'}),
        }
from django import forms
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from .models import Course

class CourseForm(forms.ModelForm):
    password_confirmation = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter password'}),
    )

    class Meta:
        model = Course
        fields = ['course_name', 'number_of_questions', 'total_marks', 'time_duration', 'exam_password']
        widgets = {
            'exam_password': forms.PasswordInput(attrs={'placeholder': 'Enter a secure password'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("exam_password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if password != password_confirmation:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        course = super().save(commit=False)
        if self.cleaned_data['exam_password']:
            course.exam_password = make_password(self.cleaned_data['exam_password'])  # Hash the password
        if commit:
            course.save()
        return course
   
