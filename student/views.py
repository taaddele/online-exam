from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from .forms import StudentUserForm
from django.forms import ValidationError
from django.contrib.auth import logout,login
from django.contrib.auth import password_validation
from django.contrib import messages
from exam import models as QMODEL
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse
from .models import CustomUser
from exam.forms import QuestionForm
from exam.models import StudentAnswer
from django.shortcuts import get_object_or_404,redirect
from django.contrib.auth.hashers import check_password
from django.views.generic import ListView
from exam.models import Result
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
# def delete_cookie_after_view(view_func):
#     def _wrapped_view(request, *args, **kwargs):
#         response = view_func(request, *args, **kwargs)
#         cookie_names = ['1','2','3','pk']
#         for cookies in cookie_names:
#          response.delete_cookie(cookies)
#          return response
#     return _wrapped_view
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')
"""def is_student(user):
    if user.is_staff:
        return False
    return user.groups.filter(name='STUDENT').exists()"""
def studentsignup_view(request):
    userForm=StudentUserForm()
    
    #studentForm=forms.StudentForm()
    #mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=StudentUserForm(request.POST)
        password = request.POST['password1']
        confirm_password = request.POST['password2']
        #studentForm=forms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and password == confirm_password:
            user=userForm.save()
            user.set_password(password)
            user.save()
            messages.success(request, 'student with name  {}  added.'.format(userForm.cleaned_data.get('first_name')))
            return HttpResponseRedirect('studentlogin')
        else:
            return render(request,'student/studentsignup.html',{'form':userForm})
    return render(request,'student/studentsignup.html',{'form':userForm})
@login_required(login_url='studentlogin')

def studentdashboard_view(request):
    # Get the logged-in student
    student = request.user

    # Get all courses
    all_courses = QMODEL.Course.objects.all()

    # Get the IDs of courses the student has already attempted
    attempted_courses_ids = QMODEL.ExamAttempt.objects.filter(user=student).values_list('pk', flat=True)

    # Filter available courses by excluding the attempted ones
    available_courses = all_courses.exclude(id__in=attempted_courses_ids)

    dict = {
        'total_course': available_courses.count(),  # Only count available courses
        'total_question': QMODEL.Question.objects.filter(course__in=available_courses).count(),  # Total questions in available courses
    }

    return render(request, 'student/studentdashboard.html', context=dict)

def logout_view(request):
    logout(request)
    return render(request,'exam/index.html')
@login_required(login_url='studentlogin')

def student_exam_view(request):
    courses = QMODEL.Course.objects.all()
    
    # Get all the courses where the user has already attempted the exam
    attempted_courses = QMODEL.ExamAttempt.objects.filter(user=request.user).values_list('course', flat=True)
    
    # Filter out the courses that the user has already attempted
    available_courses = courses.exclude(id__in=attempted_courses)

    return render(request, 'student/student_exam.html', {'courses': available_courses})


@login_required(login_url='studentlogin')

def take_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    total_questions=QMODEL.Question.objects.all().filter(course=course).count()
    questions=QMODEL.Question.objects.all().filter(course=course)
    
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks
    
    return render(request,'student/take_exam.html',{'course':course,'total_questions':total_questions,'total_marks':total_marks})
@login_required(login_url='studentlogin')

def start_exam_view(request,pk1):
    try:
        
        course=QMODEL.Course.objects.get(id=pk1)
        questions=QMODEL.Question.objects.all().filter(course=course)
        # check for existing attempt
        existing_attempt = QMODEL.ExamAttempt.objects.filter(user=request.user, course= course).first()
        
        if existing_attempt:
            attempt = existing_attempt
            
        else:
            attempt, created = QMODEL.ExamAttempt.objects.get_or_create(
                user = request.user,
                course = course,
                defaults = {'start_time':timezone.now()} 
            )
            
            if created:
                attempt.end_time = attempt.start_time+ timezone.timedelta(minutes = course.time_duration)
                attempt.save()
        
        remaining_time = (attempt.end_time-timezone.now()).total_seconds()
        if remaining_time <=0:
            return HttpResponse('exam over')
        context = {

            'remaining_time':remaining_time,
            'course':course,
            'questions':questions,

        }
        if request.method == 'POST':
                pass 
          
                # Access selected radio button values
                #for question in form.questions:  # Assuming questions list is in form instance
                   # selected_answer = request.POST.get(f'question_{question.id}')
                    #print(f"Question {question.id}: {selected_answer}")  # Print for verification

                # Process form data (e.g., save answers to database)
                # ... (your logic to save answers)

        
        response= render(request,'student/start_exam.html',context)
        return response
    except course.DoesNotExist:
        return HttpResponse("exam not found")



@login_required(login_url='studentlogin')
@csrf_exempt
def calculate_marks_view(request):
    if request.method == 'POST':
        # Retrieve the course ID from the POST data or URL parameter instead of cookies
        pk = request.POST.get('pk')  # Ensure the pk is part of the form data
        print(pk)
        # Retrieve the course object using the ID
        course = QMODEL.Course.objects.get(id=pk)

        total_marks = 0
        questions = QMODEL.Question.objects.filter(course=course)

        # Save answers to the database
        for question in questions:
            selected_answer = request.POST.get(f'question_{question.id}')
            if selected_answer:
                # Save each selected answer in the database
                StudentAnswer.objects.update_or_create(
                    student=request.user,
                    question=question,
                    defaults={'selected_answer': selected_answer}
                )

                # Calculate marks based on the saved answer
                if selected_answer == question.get_answer_text():
                    total_marks += question.marks

        # Save the result
        result, created = QMODEL.Result.objects.get_or_create(
            student=request.user,
            exam=course,
            defaults={'marks': total_marks}
        )

        if not created:
            result.marks = total_marks
            result.save()

        # Redirect to the result page
        return HttpResponseRedirect('view_result')

@login_required(login_url='studentlogin')
def view_result_view(request):
    courses=QMODEL.Course.objects.all()
   
    return render(request,'student/view_result.html',{'courses':courses})
@login_required(login_url='studentlogin')
def check_marks_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)

    student =CustomUser.objects.get(id_no=request.user.id_no)
    results= QMODEL.Result.objects.all().filter(exam=course).filter(student=student)
    return render(request,'student/check_marks.html',{'results':results,'total_questions':course})
@login_required(login_url='studentlogin')

def student_marks_view(request):
    courses=QMODEL.Course.objects.all()
    
    return render(request,'student/student_marks.html',{'courses':courses})
def enter_exam_view(request, pk):
    course = get_object_or_404(QMODEL.Course, id=pk)
    message =""
    if request.method == 'POST':
        entered_password = request.POST.get('exam_password')
        print(f"Entered Password: '{entered_password}'")
        print(f"Stored Password: '{course.exam_password}'") 
        if check_password(entered_password, course.exam_password):
            # Redirect to the exam page
            return HttpResponseRedirect(f'/student/take-exam/{pk}')  # Replace 'exam_page' with the actual view name
        else:
            message = "please enter correct exam password!!"
            

    return render(request, 'student/enter_exam.html',
                   {'course': course,
                    'message':message})