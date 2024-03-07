from rest_framework import permissions
from rest_framework.permissions import BasePermission
from .models import Professor

class IsProfessorOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow professors or admins to create professors.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Check if the user is a professor or an admin
        try:
            professor = Professor.objects.get(user=request.user)
            return professor.is_admin
        except Professor.DoesNotExist:
            return False

class CanRegisterProfessor(BasePermission):
   """
    Custom permission to allow only admins or professors to register new professors.
    """
   def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Check if the user is an admin or a professor
        return request.user.is_admin or request.user.is_professor