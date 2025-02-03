from django.urls import path
from teacher import views
from django.contrib.auth.views import LoginView

from django.urls import path
from teacher import views
from django.contrib.auth.views import LoginView
from .views import CustomLoginView
from .views import StudentResultView
urlpatterns = [
path('teacherclick', views.teacherclick_view),
path('teacherlogin', CustomLoginView.as_view(template_name='teacher/teacherlogin.html'),name='teacherlogin'),
path('teachersignup', views.teacher_signup_view,name='teachersignup'),
path('teacher-dashboard/', views.teacher_dashboard_view,name='teacher-dashboard'),
path('teacher-exam', views.teacher_exam_view,name='teacher-exam'),
path('teacher-add-exam', views.teacher_add_exam_view,name='teacher-add-exam'),
path('teacher-view-exam', views.teacher_view_exam_view,name='teacher-view-exam'),
path('delete-exam/<int:pk>', views.delete_exam_view,name='delete-exam'),
path('manage-students/', views.manage_students_view, name='manage_students'),
path('add-student/', views.add_student_view, name='add_student'),

path('teacher-question', views.teacher_question_view,name='teacher-question'),
path('teacher-add-question', views.teacher_add_question_view,name='teacher-add-question'),
path('teacher-view-question', views.teacher_view_question_view,name='teacher-view-question'),
path('see-question/<int:pk>', views.see_question_view,name='see-question'),
path('remove-question/<int:pk>', views.remove_question_view,name='remove-question'),
path('edit_student/<int:pk>/', views.edit_student_view, name='edit_student'),
path('delete_student/<int:pk>/', views.delete_student_view, name='delete_student'),
path('exam-attempts/', views.exam_attempts_view, name='exam-attempts'),
path('delete-exam-attempt/<int:pk>/', views.delete_exam_attempt, name='delete_exam_attempt'),
path('student-results', StudentResultView.as_view(), name='student-results'),
path('student-answer', views.student_answers_view, name='student-answer'),
path('view-answer',views.view_student_view, name= 'view-answer'),
path('view-student-answer/<int:pk>/',views.view_student_answer_view, name= 'view-student-answer'),
path('view-student-results/<int:pk>/',views.view_student_result_view, name='view-student-results'),
path('edit_question/<int:pk>/', views.edit_question_view, name='edit_question'),
path('edit-course/<int:pk>/', views.edit_course_view, name='edit-course'),
] 