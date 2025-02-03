from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required,user_passes_test
# Create your views here.
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')  
    return render(request,'exam/index.html')
def afterlogin_view(request):
    if request.user.is_staff and request.user.is_superuser:     
        return HttpResponseRedirect('admin')
    elif request.user.is_staff:
        return redirect('teacher/teacher-dashboard')
    else:
        return redirect('student/student-dashboard')   
def logout_view(request):
    logout(request)
    return render(request,'exam/index.html')
def adminclick_view(request):
    return HttpResponseRedirect('admin')