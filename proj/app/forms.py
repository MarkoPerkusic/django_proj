from django import forms
from .models import Professor
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfessorCreationForm(forms.ModelForm):
    user = forms.CharField(max_length=150)

    class Meta:
        model = Professor
        fields = '__all__'
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            # Check if the user with the provided username exists
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # If the user does not exist, raise a validation error
            raise forms.ValidationError("The specified username does not exist.")
        return username
