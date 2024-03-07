from django.contrib import admin
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from .models import Enrollment, Professor
from .views import approve_enrollment, reject_enrollment
from .forms import ProfessorCreationForm

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'admin')
    actions = ['approve_selected_enrollments']

    def approve_selected_enrollments(self, request, queryset):
        for enrollment in queryset:
            # Set the admin field to the currently logged-in admin user
            enrollment.admin = request.user 
            enrollment.save() 
        
        self.message_user(request, f"{len(queryset)} enrollment(s) approved successfully.")
        return HttpResponseRedirect(reverse('admin:app_enrollment_changelist'))

    approve_selected_enrollments.short_description = _("Approve selected enrollments")

    def save_model(self, request, obj, form, change):
        """
        Intercept saving of enrollment model instance and perform additional actions.

        Args:
            self: The object itself.
            request: The request object.
            obj: The enrollment model instance being saved.
            form: The form instance used to edit the enrollment model instance.
            change: A boolean value indicating whether the model instance is being edited or created.

        Returns:
            None
        """

        # Fill the admin field with the current user if it's not already set
        if not obj.admin:
            obj.admin = request.user

        # Call the parent class's save_model method to save the model instance
        super().save_model(request, obj, form, change)

        # Perform additional actions after saving the model instance
        if obj.status == Enrollment.APPROVED:
            approve_enrollment(request, obj)
        elif obj.status == Enrollment.REJECTED:
            reject_enrollment(request, obj)


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    form = ProfessorCreationForm