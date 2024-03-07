from django.urls import path
from . import views

urlpatterns = [
    
    path('login/',  views.login, name='login'),
    path('refresh/', views.refresh_token, name='refresh_token'),
    path('student/register/',  views.student_registration, name='student_registration'),
    path('student/<int:id>/profile/',  views.student_profile, name='student_profile'),
    path('student/<int:id>/courses/', views.courses_and_subjects, name='courses_and_subjects'),
    path('student/<int:student_id>/course_enrollment/', views.course_enrollment, name='course_enrollment'),
    path('students/', views.student_list, name='student_list'),
    path('professor/register/',  views.professor_registration, name='professor_registration'),
    path('professor/<int:user_id>/profile/',  views.professor_profile, name='professor_profile'),
    path('course/<int:course_id>/subjects/',  views.subject_list, name='course_subjects'),
]
