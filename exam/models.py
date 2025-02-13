from django.db import models
from django.utils.timezone import now
from datetime import timedelta
from student.models import CustomUser
# Create your models here.
class Course(models.Model):
   course_name = models.CharField(max_length=50)
   number_of_questions = models.PositiveIntegerField()
   total_marks = models.PositiveIntegerField(default=None)
   time_duration = models.PositiveIntegerField(default=None)
   exam_password = models.CharField(max_length=20, null=True, blank=True)  # Field for exam password
   class Meta:
       verbose_name = "course"
    
   def __str__(self): 
        return self.course_name
class Question(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    marks=models.PositiveIntegerField()
    question=models.CharField(max_length=600)
    option1=models.CharField(max_length=200)
    option2=models.CharField(max_length=200)
    option3=models.CharField(max_length=200)
    option4=models.CharField(max_length=200)
    cat=(('Option1','Option1'),('Option2','Option2'),('Option3','Option3'),('Option4','Option4'))
    answer=models.CharField(max_length=200,choices=cat)
    class Meta:
        verbose_name ='question'
        verbose_name_plural = 'questions'
    def __str__(self):
        return self.question
    # Method to retrieve the actual answer text based on the 'answer' value
    def get_answer_text(self):
        if self.answer == 'Option1':
            return self.option1
        elif self.answer == 'Option2':
            return self.option2
        elif self.answer == 'Option3':
            return self.option3
        elif self.answer == 'Option4':
            return self.option4
        return None  # in case there's no answer (although that shouldn't happen)
class Result(models.Model):
    student = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    exam = models.ForeignKey(Course,on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "result"
        unique_together = ('student', 'exam')
    def __str__(self):
        return self.student.first_name
class ExamAttempt(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null = True, blank=True)
    class Meta:
        verbose_name = 'ExamAttempt'
    def __str__(self):
        return self.user.first_name
# student answer stored in this class
class StudentAnswer(models.Model):
    student = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=700)
    class Meta:
        verbose_name = 'student Answers'
    def __str__(self):
        return self.student.first_name

