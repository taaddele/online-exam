from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from datetime import date, timedelta
from exam import models as QMODEL
from student import models as SMODEL
from exam import forms as QFORM
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
from .forms import StudentSearchForm, TeacherUserForm
from student.models import CustomUser
from student.forms import UserChangeForm
from django.shortcuts import render, get_object_or_404
from .forms import CustomUserForm
from django.views.generic import ListView
from exam.models import Result
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
#for showing signup/login button for teacher
def teacherclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'teacher/teacherclick.html')

def teacher_signup_view(request):
    userForm=forms.TeacherUserForm()

    mydict={'userForm':userForm}
    if request.method=='POST':
        userForm=forms.TeacherUserForm(request.POST)
        password = request.POST['password1']
        confirm_password = request.POST['password2']
        if userForm.is_valid()and password==confirm_password: 
            user=userForm.save(commit=False)
            user.is_staff =True
            user.set_password(password)
            user.save()
        
        return HttpResponseRedirect('teacherlogin')
    return render(request,'teacher/teachersignup.html',context=mydict)



def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()

@login_required(login_url='teacherlogin')

def teacher_dashboard_view(request):
    dict={
    
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    'total_student':SMODEL.CustomUser.objects.all().filter(departement = request.user.departement).exclude(id_no = request.user.id_no).count()
    }
    return render(request,'teacher/teacher_dashboard.html',context=dict)

@login_required(login_url='teacherlogin')

def teacher_exam_view(request):
    return render(request,'teacher/teacher_exam.html')


@login_required(login_url='teacherlogin')

def teacher_add_exam_view(request):
    courseForm = QFORM.CourseForm()
    if request.method == 'POST':
        courseForm = QFORM.CourseForm(request.POST)
        if courseForm.is_valid():
            courseForm.save()
            return HttpResponseRedirect('/teacher/teacher-view-exam')
        else:
            print(courseForm.errors)  # Debugging output for invalid forms
    return render(request, 'teacher/teacher_add_exam.html', {'courseForm': courseForm})

@login_required(login_url='teacherlogin')

def teacher_view_exam_view(request):
    courses = QMODEL.Course.objects.all()
    return render(request,'teacher/teacher_view_exam.html',{'courses':courses})


@login_required(login_url='teacherlogin')
def delete_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/teacher/teacher-view-exam')

@login_required(login_url='adminlogin')
def teacher_question_view(request):
    return render(request,'teacher/teacher_question.html')

@login_required(login_url='teacherlogin')


def teacher_add_question_view(request):
    questionForm = QFORM.QuestionForm()

    if request.method == 'POST':
        questionForm = QFORM.QuestionForm(request.POST)

        if questionForm.is_valid():
            question = questionForm.save(commit=False)
            # Get the selected course
            course = question.course
            # Count the existing questions for this course
            current_question_count = QMODEL.Question.objects.filter(course=course).count()

            # Check if adding this question would exceed the limit
            if current_question_count >= course.number_of_questions:
                # Add an error message and re-render the form
                messages.error(
                    request,
                    f"Cannot add more questions. The limit for this course ({course.number_of_questions} questions) has been reached."
                )
                return render(request, 'teacher/teacher_add_question.html', {
                    'questionForm': questionForm
                })

            # Save the question if within the limit
            question.save()

            if 'add_another' in request.POST:
                # Success message for adding another question
                messages.success(request, "Question added successfully. Add another!")
                return render(request, 'teacher/teacher_add_question.html', {
                    'questionForm': QFORM.QuestionForm()
                })
            else:
                # Redirect to view questions
                messages.success(request, "Question added successfully.")
                return HttpResponseRedirect('/teacher/teacher-view-question')
        else:
            # If form is invalid, show an error
            messages.error(request, "There were errors in your form. Please fix them and try again.")
            
    return render(request, 'teacher/teacher_add_question.html', {'questionForm': questionForm})

@login_required(login_url='teacherlogin')

def teacher_view_question_view(request):
    courses= QMODEL.Course.objects.all()
    return render(request,'teacher/teacher_view_question.html',{'courses':courses})

@login_required(login_url='teacherlogin')

def see_question_view(request,pk):
    questions=QMODEL.Question.objects.all().filter(course_id=pk)
    return render(request,'teacher/see_question.html',{'questions':questions})

@login_required(login_url='teacherlogin')

def remove_question_view(request, pk):
    question = QMODEL.Question.objects.get(id=pk)
    question.delete()
    # Redirect back to the referring page or fallback to a default URL
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/teacher/see-question'))
class CustomLoginView(LoginView):
    template_name = 'teacher/teacherlogin.html'  # Adjust for each type of user

    def get_success_url(self):
        user = self.request.user
        if user.is_staff:
            return '/teacher/teacher-dashboard'
        else :
            return '/student/student-dashboard'
        # Add more roles or conditions here if needed
        return super().get_success_url()  # Fallback to default behavior
@login_required

def manage_students_view(request):

    user_department = request.user.departement
    search_form = StudentSearchForm(request.GET)
    students = CustomUser.objects.all().filter(departement = user_department).exclude(id_no = request.user.id_no)
    
    if request.GET.get('search_term'):
         search_term = request.GET['search_term']
        
        # Filter based on search input (try to match it with ID, first name, or last name)
         if search_term.isdigit():  # If search term is a number, filter by ID
            students = students.filter(id_no__icontains=search_term)
         else:
            students = students.filter(
                first_name__icontains=search_term
            ) | students.filter(
                last_name__icontains=search_term
            )
    if not students.exists():
        message = "There is No registered user under you."
    else:
        message = ""
    return render(request, 'teacher/manage_students.html', 
                  {'students': students, 
                   'search_form': search_form,
                   'message': message})

@login_required

def add_student_view(request):
    if request.method == 'POST':
        form = TeacherUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('teacher/manage_students')  # Redirect back to the student list page
    else:
        form = TeacherUserForm()

    return render(request, 'teacher/add_student.html', {'form': form})
def edit_student_view(request, pk):
    student = get_object_or_404(CustomUser, id_no=pk)
    
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=student)
        if form.is_valid():
            form.save()  # Save the updated student data
            return redirect('manage-students')  # Redirect to some success page or back to the list
    else:
        form = CustomUserForm(instance=student)

    return render(request, 'teacher/edit_student.html', {'form': form})

def delete_student_view(request, pk):
    student=CustomUser.objects.get(id_no=pk)
    student.delete()
    return HttpResponseRedirect('/teacher/manage-students')
@login_required
def exam_attempts_view(request):
    # Get all exam attempts
    exam_attempts = QMODEL.ExamAttempt.objects.all()

    return render(request, 'teacher/exam_attempts.html', {'exam_attempts': exam_attempts})

@login_required
def delete_exam_attempt(request, pk):
    # Get the exam attempt by pk
    exam_attempt = get_object_or_404(QMODEL.ExamAttempt, pk=pk)

    # Delete the exam attempt
    exam_attempt.delete()

    # Redirect to the list of exam attempts
    return redirect('exam-attempts')  # Replace with the appropriate URL name
class StudentResultView(LoginRequiredMixin, ListView):
    model = Result
    template_name = 'teacher/student_result.html'
    context_object_name = 'results'
   
    def get_queryset(self):
        # Fetch results for the logged-in teacher's students only
        # You can filter the results by exam if needed
        return Result.objects.all()  # Assuming the teacher is associated with the exam
@login_required
def student_answers_view(request):
    # Optionally filter answers for a specific teacher's students or course
    student_answers = QMODEL.StudentAnswer.objects.all()

    return render(request, 'teacher/student_answers.html', {'student_answers': student_answers})
def view_student_view(request):
         user_department = request.user.departement
         search_form = StudentSearchForm(request.GET)
         students = CustomUser.objects.all().filter(departement = user_department).exclude(id_no = request.user.id_no)
    
         if request.GET.get('search_term'):
            search_term = request.GET['search_term']
            
            # Filter based on search input (try to match it with ID, first name, or last name)
            if search_term.isdigit():  # If search term is a number, filter by ID
                students = students.filter(id_no__icontains=search_term)
            else:
                students = students.filter(
                    first_name__icontains=search_term
                ) | students.filter(
                    last_name__icontains=search_term
                )
         if not students.exists():
            message = "There is No student taken an exam under you."
         else:
            message = ""
         return render(request, 'teacher/view_student.html',
                       {'students': students, 
                        'search_form': search_form,
                        'message':message}) 
def view_student_answer_view(request, pk):
     student = get_object_or_404(CustomUser, id_no=pk)
     students = QMODEL.StudentAnswer.objects.filter(student = student)
     return render(request,'teacher/view_student_answer.html',{'students':students})
def view_student_result_view(request,pk):
    student = get_object_or_404(CustomUser, id_no=pk)
    result = Result.objects.filter(student = student)
    return render(request,'teacher/student_result.html',{'results':result})
def edit_question_view(request, pk):
    question = get_object_or_404(QMODEL.Question, id=pk)
    message = ""
    if request.method == 'POST':
        form = QFORM.QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()  # Save the updated student data
            message = "you updated successfully"
            return render(request, 'teacher/edit_question.html', 
                          {'form': form,
                           'message':message}) # Redirect to some success page or back to the list
    else:
        form = QFORM.QuestionForm(instance=question)

    return render(request, 'teacher/edit_question.html', {'form': form})
def edit_course_view(request,pk):
    course = get_object_or_404(QMODEL.Course, id=pk)
    message = ""
    if request.method == 'POST':
        form = QFORM.CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()  # Save the updated student data
            message = "you updated successfully"
            return render(request, 'teacher/edit_course.html', 
                          {'form': form,
                           'message':message}) # Redirect to some success page or back to the list
    else:
        form = QFORM.CourseForm(instance=course)

    return render(request, 'teacher/edit_course.html', {'form': form})
         