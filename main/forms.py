from registration.forms import RegistrationFormUniqueEmail
from django import forms

class UserRegForm(RegistrationFormUniqueEmail):
	institution = forms.CharField(max_length=100, required=False)
	orcid = forms.CharField(max_length=100, required=False, label='ORCID')