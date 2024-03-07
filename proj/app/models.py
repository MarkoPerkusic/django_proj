from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.forms import ValidationError

class CourseType(models.Model):
    name = models.CharField(max_length=100)

class Course(models.Model):
    name = models.CharField(max_length=100)
    course_type = models.ForeignKey(CourseType, on_delete=models.CASCADE)
    # Maximum number of students allowed in the course
    max_capacity = models.PositiveIntegerField(default=0)
    # Current number of enrolled students 
    current_capacity = models.PositiveIntegerField(default=0)  

    def save(self, *args, **kwargs):
        # Check if a course with the same name and course type already exists
        if Course.objects.filter(name=self.name, course_type=self.course_type).exists():
            # If it exists, raise a validation error
            raise ValidationError("A course with the same name and course type already exists.")
        super().save(*args, **kwargs)

class Subject(models.Model):
    description = models.CharField(max_length=300)
    ects_points = models.IntegerField(default=1)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class UserProfile(AbstractUser):
    email = models.EmailField(unique=True)
    username = None
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_professor = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Student(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, related_name='students')
    place_of_birth = models.CharField(max_length=100, null=True, blank=True)
    school = models.CharField(max_length=100, default="")
    average_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self):
        return self.user.email

class Professor(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, primary_key=True)
    is_admin = models.BooleanField(default=False)

class Enrollment(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.student} - {self.course} - {self.status}"