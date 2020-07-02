from django import forms
from django.forms.models import inlineformset_factory
from .models import Course, Module

#extra - allows us to set the number of empty extra forms to display in the formset
#can_delete - Django will include a Boolean field for each form that will be rendered as a checkbox input. It allows you to mark the objects you want to delete.
ModuleFormSet = inlineformset_factory(Course, Module, fields = ['title', 'description'], extra = 2, can_delete = True)

