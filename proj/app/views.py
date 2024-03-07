# myapp/views.py

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .permissions import IsProfessorOrAdmin

from .models import Course, Enrollment, Subject, Student, Professor
from .serializers import CourseEnrollmentSerializer, UserProfile, CourseSerializer, SubjectSerializer, StudentSerializer, ProfessorSerializer, StudentRegistrationSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import permission_required
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import F



@api_view(['POST'])
def login(request):
    """
    A view for user login using email and password. 
    Accepts a POST request with email and password in the request data. 
    Returns tokens for authentication if the user is valid, else returns an error message.
    """

    email = request.data.get('email')
    password = request.data.get('password')

    # Authenticate user
    user = authenticate(email=email, password=password)

    if user is not None:
        # User is authenticated, generate tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id
        }, status=status.HTTP_200_OK)
    else:
        # Authentication failed
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['POST'])
def refresh_token(request):
    refresh_token = request.data.get('refresh')

    if refresh_token is None:
        return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)
        access_token = token.access_token
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    return Response({'access': str(access_token)})

#################################STUDENTS####################################################
@api_view(['POST'])
def student_registration(request):
    """
    A view for registering a student, which accepts a POST request. 
    It saves the student data, including the course field, and returns the user ID if the data is valid. Otherwise, it returns the serializer errors with a 400 status code.
    """
    
    if request.method == 'POST':
        # Make a copy of the request data
        data = request.data.copy()

        # Check if 'course' field is not provided, and set it to None
        if 'course' not in data:
            data['course'] = ''

        student_serializer = StudentRegistrationSerializer(data=data)
        if student_serializer.is_valid():
            user = student_serializer.save()
            return Response({'user_id': user.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def student_profile(request, id):
    """
    A view function for handling GET and PUT requests for a student profile. 
    It checks if the authenticated user is the owner of the profile being accessed, 
    and returns the student profile information or allows updating it based on the request method.
    """
        
    try:
        student = Student.objects.get(pk=id)
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the authenticated user is the owner of the profile being accessed
    if request.user.id != student.user.id:
        return Response({'error': 'You are not authorized to access this profile'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = StudentSerializer(student)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = StudentSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def courses_and_subjects(request, id):
    """
    Retrieves courses and subjects for a student and returns the data as a response.
    
    Parameters:
    - request: the request object
    - id: the ID of the student
    
    Returns:
    - Response: the response object with course data or error message
    """
    
    try:
        student = Student.objects.get(pk=id)
        if student.course:
            courses = student.course.all()
            course_data = []
            for course in courses:
                course_info = {
                    'id': course.id,
                    'name': course.name,
                    'subjects': [subject.name for subject in course.subject_set.all()]
                }
                course_data.append(course_info)
            return Response(course_data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No courses found for this student'}, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def course_enrollment(request, student_id):
    """
    Function for handling course enrollment for a student.

    Parameters:
    - request: the HTTP request object
    - student_id: the ID of the student enrolling in the course

    Return types:
    - Response: HTTP response object
    """

    try:
        student = Student.objects.get(pk=student_id)
        serializer = CourseEnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            course_id = serializer.validated_data.get('course_id')
            course = Course.objects.get(pk=course_id)
            
            # Check if there is a free place available in the course
            if course.current_capacity < course.max_capacity:
                # Create a pending enrollment request
                enrollment = Enrollment.objects.create(student=student, course=course, status='pending')
                
                # Update the course field of the student
                student.course = course
                student.save()
                
                # Provide feedback to the student about the enrollment request
                return Response({'message': 'Enrollment request created. Waiting for admin approval.'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Course is full. Enrollment request not created.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except (Student.DoesNotExist, Course.DoesNotExist):
        return Response({'error': 'Student or course not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
#@permission_classes([IsAdminUser])
def approve_enrollment(request, enrollment):
    """
    A view to approve an enrollment.

    Parameters:
    - request: the HTTP request object
    - enrollment: the Enrollment object to be approved

    Returns:
    - HttpResponse: a response indicating the result of the approval process
    """
    try:
        # Ensure that the user is authenticated and is a UserProfile instance
        if request.user.is_authenticated and isinstance(request.user, UserProfile):
            course = enrollment.course

            # Increment current_capacity if it doesn't exceed max_capacity
            if course.current_capacity < course.max_capacity:
                # Increment current_capacity using F() expression to avoid race conditions
                Course.objects.filter(pk=course.pk).update(current_capacity=F('current_capacity') + 1)

                # Update enrollment status and admin
                enrollment.status = Enrollment.APPROVED
                # Set the admin field to the currently logged-in admin user
                enrollment.admin = request.user  
                enrollment.save()

                return HttpResponse("Enrollment approved successfully")
            else:
                return HttpResponse("Course is already full")
        else:
            return HttpResponse("User is not authenticated or is not a UserProfile instance")
    except Enrollment.DoesNotExist:
        return HttpResponse("Enrollment request not found")


@api_view(['POST'])
@permission_classes([IsAdminUser])
def reject_enrollment(request, enrollment_id):
    """
    Endpoint for rejecting an enrollment request.
    
    Parameters:
    - request: the HTTP request object
    - enrollment_id: the ID of the enrollment to be rejected
    
    Returns:
    - Response({'message': 'Enrollment request rejected'}, status=status.HTTP_200_OK) if enrollment is successfully rejected
    - Response({'error': 'Enrollment request not found'}, status=status.HTTP_404_NOT_FOUND) if the enrollment does not exist
    """

    try:
        enrollment = Enrollment.objects.get(pk=enrollment_id)
        enrollment.status = Enrollment.REJECTED
        enrollment.admin = request.user
        enrollment.save()
        return Response({'message': 'Enrollment request rejected'}, status=status.HTTP_200_OK)
    except Enrollment.DoesNotExist:
        return Response({'error': 'Enrollment request not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_list(request):
    """
    Get the list of students and return it as serialized data.
    """
    students = Student.objects.all()
    serializer = StudentSerializer(students, many=True)
    return Response(serializer.data)

#################################SUBJECTS####################################################
@api_view(['POST'])
def create_subject(request):
    """
    Create a new subject using the data from the request. 

    Parameters:
    - request: The HTTP request object containing the data for the new subject.

    Returns:
    - Response: The HTTP response object containing the result of the subject creation.
    """

    serializer = SubjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def subject_list(request, course_id):
    """
    Retrieve subjects for the specified course ID
    """
    
    try:
        subjects = Subject.objects.filter(course_id=course_id)
    except Subject.DoesNotExist:
        return Response({'error': 'Subjects not found'}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the subjects data
    serializer = SubjectSerializer(subjects, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

#################################COURSESS####################################################

@api_view(['POST'])
def create_course(request):
    """
    Create a new course using the data from the request. 
    The function takes a request object and returns a success response if the data is valid. 
    If the data is not valid, it returns an error response.
    """

    serializer = CourseSerializer(data=request.data)

    # Validate the data
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        # Return an error response if data is not valid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_course(request, course_id):
    """
    A function to update the course using PUT method.
    """

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    # Deserialize the data from the request, passing the existing course object
    serializer = CourseSerializer(instance=course, data=request.data)

    # Validate and save the updated course data
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_course(request, course_id):
    """
    A view that deletes a course based on the provided course_id.
    """
    
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    # Delete the course
    course.delete()
    return Response({'message': 'Course deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


#################################PROFESSORSS####################################################

@api_view(['POST'])
@permission_classes([AllowAny])
def professor_registration(request):
    """
    A function for registering a professor.
    It takes a POST request and extracts username, password, and email from the request data.
    It then creates a new user and a new professor profile using the extracted data,
    serializes the professor data, and returns the serialized professor data with a HTTP 201 Created status.
    """
    data = request.data
    password = data.get('password')
    email = data.get('email')

    # Create a new user
    user = UserProfile.objects.create_user(password=password, email=email)

    # Create a new professor profile
    professor = Professor.objects.create(user=user, is_admin=True)

    # Serialize the professor data
    serializer = ProfessorSerializer(professor)

    # Return the serialized professor data
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsProfessorOrAdmin])
def professor_profile(request, user_id):
    """
    Get the professor profile for the specified ID and return it as serialized data.
    """
    
    # Retrieve the professor profile based on the ID
    try:
        professor = Professor.objects.get(user_id=user_id)
    except Professor.DoesNotExist:
        return Response({'error': 'Professor profile not found'}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the professor profile data
    serializer = ProfessorSerializer(professor)

    # Return the serialized professor profile data
    return Response(serializer.data, status=status.HTTP_200_OK)
