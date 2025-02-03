from django.contrib import admin
from exam.models import Question,Course,Result
from student.models import CustomUser
# Register your models here.
admin.site.register(Question)
admin.site.register(Course)
admin.site.register(Result)