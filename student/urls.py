from django.urls import path
from student import views
from django.contrib.auth.views import LoginView

urlpatterns = [
path('studentclick', views.studentclick_view),
path('studentsignup',views.studentsignup_view),
path('studentlogin', LoginView.as_view(template_name='student/studentlogin.html'),name='studentlogin'),
path('student-dashboard', views.studentdashboard_view),
path('logout',views.logout_view),
path('student-exam',views.student_exam_view, name= 'student_exam_view'),
path('take-exam/<int:pk>', views.take_exam_view,name='take-exam'),
path('enter-exam/<int:pk>', views.enter_exam_view,name='enter-exam'),
path('start-exam/<int:pk1>', views.start_exam_view,name='start-exam'),
path('calculate-marks', views.calculate_marks_view,name='calculate-marks'),
path('view_result', views.view_result_view,name='view-result'),
path('check-marks/<int:pk>', views.check_marks_view,name='check-marks'),
path('student-marks', views.student_marks_view,name='student-marks'),

]