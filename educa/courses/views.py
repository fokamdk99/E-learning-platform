from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Course
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# Create your views here.

class ManageCourseListView(ListView):
    model = Course
    template_name = "/manage/course/list.html"

    def get_queryset(self):
        print("cos sie dzieje")
        #get only courses created by the current user
        qs = super(ManageCourseListView, self).get_queryset()
        return qs.filter(owner = self.request.user)

#used for views that interact with any model that contains an 'owner' attribute
class OwnerMixin(object):
    def get_queryset(self):
        #chyba get_queryset(pobiera wszystkie elementy z bazy??)
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)

#set the owner for an object automatically when it is saved
class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)

#provides 'model' attribute for child views that is used for querysets
class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')

#
class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    #fields of the model to build the model form of CreateView and UpdateView views
    fields = ['subject', 'title', 'slug', 'overview']
    #url used by CreateView and UpdateView to redirect the user after the form is successfully submitted
    success_url = reverse_lazy('manage_course_list')
    template_name = "courses/manage/course/form.html"

#ponizsze funkcje sa dostepne tylko dla uzytkownikow z uprawnieniami
#list the courses created by the user
class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
'''
Uses a modelform to create a new Course object.
It uses the fields defined in OwnerCourseEditMixin to build a model
CourseCreateView form'''
class CourseCreateView(PermissionRequiredMixin, OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'

#Allows editing an existing Course object.
class CourseUpdateView(PermissionRequiredMixin, OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'

#Defines success_url to redirect the user after the CourseDeleteView object is deleted.
class CourseDeleteView(PermissionRequiredMixin, OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    success_url = reverse_lazy('manage_course_list')
    permission_required = 'courses.delete_course'

'''
Mixins are a special kind of multiple inheritance for a class. You can
use them to provide common discrete functionality that, added to
other mixins, allows you to define the behavior of a class. There are
two main situations to use mixins:
1) You want to provide multiple optional features for a class
2) You want to use a particular feature in several classes
'''