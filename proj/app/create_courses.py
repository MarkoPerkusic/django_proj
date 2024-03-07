import os
import django
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
django.setup()

from app.models import CourseType, Course, Subject

def create_course_types():
    # Create course types
    CourseType.objects.bulk_create([
        CourseType(name='Tehnoloski'),
        CourseType(name='Informaticki'),
        CourseType(name='Matematicki'),
    ])

def create_courses():
    # Get course types
    tehnoloski_course_type = CourseType.objects.get(name='Tehnoloski')
    informaticki_course_type = CourseType.objects.get(name='Informaticki')
    matematicki_course_type = CourseType.objects.get(name='Matematicki')

    # Create courses
    Course.objects.bulk_create([
        Course(name='Course1', course_type=tehnoloski_course_type, max_capacity=20),
        Course(name='Course2', course_type=informaticki_course_type, max_capacity=120),
        Course(name='Course3', course_type=matematicki_course_type, max_capacity=10),
    ])

def create_subjects():
    # Get courses
    tehnoloski_course = Course.objects.get(name='Course1')
    informaticki_course = Course.objects.get(name='Course2')
    matematicki_course = Course.objects.get(name='Course3')

    # Create subjects
    Subject.objects.bulk_create([
        Subject(description='Subject 1 for Tehnoloski', course=tehnoloski_course, ects_points=6),
        Subject(description='Subject 2 for Tehnoloski', course=tehnoloski_course, ects_points=4),
        Subject(description='Subject 3 for Tehnoloski', course=tehnoloski_course, ects_points=2),
        Subject(description='Subject 1 for Informaticki', course=informaticki_course, ects_points=5),
        Subject(description='Subject 2 for Informaticki', course=informaticki_course, ects_points=3),
        Subject(description='Subject 3 for Informaticki', course=informaticki_course, ects_points=3),
        Subject(description='Subject 4 for Informaticki', course=informaticki_course, ects_points=1),
        Subject(description='Subject 1 for Matematicki', course=matematicki_course, ects_points=7),
        Subject(description='Subject 2 for Matematicki', course=matematicki_course, ects_points=5),
    ])

if __name__ == '__main__':
    create_course_types()
    create_courses()
    create_subjects()
    print('Courses and subjects created successfully.')
