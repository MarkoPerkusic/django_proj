from rest_framework import serializers
from .models import Course, Subject, UserProfile, Student, Professor, Course, CourseType
from rest_framework_simplejwt.tokens import RefreshToken

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'course_type', 'max_capacity']
        read_only_fields = ['id']


class CourseEnrollmentSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['email', 'password', 'first_name', 'last_name']
         #['id', 'password', 'email', 'is_student', 'is_professor', 
         # 'place_of_birth', 'school', 'average_score']
        read_only_fields = ['id']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        """
        Create a new user with the provided data and return the user instance.

        Parameters:
            validated_data (dict): The validated data for creating the user.

        Returns:
            UserProfile: The newly created user instance.
        """
        
        # Extract 'password' from validated data
        password = validated_data.pop('password', None)
        # Create a new 'User' instance with provided data
        user = UserProfile.objects.create_user(**validated_data, password=password)

        return user

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['user', 'course', 'school', 'average_score', 'place_of_birth']
    
    def create(self, validated_data):
        """
        Create a new student object using the provided validated data.

        Args:
            validated_data: A dictionary containing the validated data for creating the student object.

        Returns:
            Student: The newly created Student object.
        """
        
        return Student.objects.create(**validated_data)

class StudentRegistrationSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    surname = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Student
        fields = ['name', 'surname', 'email', 'password', 'course']

    def validate_email(self, value):
        """
        Validate the email value and check if it already exists in the UserProfile objects. 
        Raises a serializers.ValidationError if a user with the email already exists. 
        Returns the email value.
        """

        if UserProfile.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def create(self, validated_data):
        """
        Create user profile and student profile using the provided validated data.
        
        Parameters:
            validated_data (dict): A dictionary containing the validated data for creating user and student profiles.
        
        Returns:
            User: The user profile created.
        """
        
        user_data = {
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password'),
            'first_name': validated_data.pop('name'),
            'last_name': validated_data.pop('surname'),
        }
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
        else:
            raise serializers.ValidationError(user_serializer.errors)

        # Create student profile
        validated_data['user'] = user.pk  # Assign user's primary key
        student_serializer = StudentSerializer(data=validated_data)
        if student_serializer.is_valid():
            student = student_serializer.save()
        else:
            raise serializers.ValidationError(student_serializer.errors)

        return user


class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = ['user', 'is_admin',]
    
    def get_token(self, obj):
        refresh = RefreshToken.for_user(obj.user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

class CourseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseType
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'course_type', 'max_capacity', 'current_capacity']
        read_only_fields = ['id']

class CourseAndDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['course', 'school', 'place_of_birth', 'average_score']

    def create(self, validated_data):
        """
        Create a new student using the validated data and return the created student instance.
        
        Parameters:
            validated_data: The validated data to create the student with.
        
        Returns:
            The created student instance.
        """
        
        # Extract course and details data
        course = validated_data.pop('course')
        # Add user information to validated data
        validated_data['user'] = self.context['request'].user
        # Create Student instance
        student = Student.objects.create(course=course, **validated_data)
        return student

class CourseSelectionSerializer(serializers.Serializer):
    course_ids = serializers.ListField(child=serializers.IntegerField())