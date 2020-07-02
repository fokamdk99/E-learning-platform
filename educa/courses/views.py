from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from .models import Course, Module, Content
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet
from django.forms.models import modelform_factory
from django.apps import apps
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
# Create your views here.

class ManageCourseListView(ListView):
    model = Course
    template_name = "/manage/course/list.html"

    def get_queryset(self):
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

class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    '''
    We define this method to avoid repeating the
    get_formset()
    code to build the formset. We create a ModuleFormSet object for
    the given Course object with optional data.
    '''
    def get_formset(self, data = None):
        return ModuleFormSet(instance = self.course, data = data)

    '''
    This method is provided by the View class. It takes
    an HTTP request and its parameters and attempts to
    delegate to a lowercase method that matches the HTTP
    method used: a GET request is delegated to the get() method
    and a POST request to post() , respectively. In this method, we
    use the get_object_or_404() shortcut function to get the Course 
    object for the given id parameter that belongs to the current
    user. We include this code in the dispatch() method because
    we need to retrieve the course for both GET and POST requests.
    We save it into the course attribute of the view to make it
    accessible to other methods.
    '''
    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course, id = pk, owner = request.user)
        return super(CourseModuleUpdateView, self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course' : self.course, 'formset' : formset})
    
    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data = request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course' : self.course, 'formset' : formset})

class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    '''
    we check that the given model name is one
    of the four content models: Text , Video , Image , or File . Then, we
    use Django's apps module to obtain the actual class for the given
    model name. If the given model name is not one of the valid
    ones, we return None .
    '''
    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label = 'courses', model_name = model_name)
        return None

    '''
    We build a dynamic form using the modelform_factory()
    function of the form's framework. Since we are going to
    build a form for the Text , Video , Image , and File models, we use
    get_form()
    the exclude parameter to specify the common fields to exclude
    from the form and let all other attributes be included
    automatically. By doing so, we don't have to know which
    fields to include depending on the model.
    '''
    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude = ['owner', 'order', 'created', 'updated'])
        return Form(*args, **kwargs)

    '''
    It receives the following URL parameters and
    stores the corresponding module, model, and content object
    as class attributes:
    1) module_id - The ID for the module that the content
    is/will be associated with.
    2) model_name - The model name of the content to create/update.
    3) id - The ID of the object that is being updated. It's None
    to create new objects.
    '''
    def dispatch(self, request, module_id, model_name, id = None):
        self.module = get_object_or_404(Module, id = module_id, course__owner = request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id = id, owner = request.user)
        return super(ContentCreateUpdateView, self).dispatch(request, module_id, model_name, id)

    '''
    We build themodel form 
    for the Text , Video , Image , or File instance that is
    being updated. Otherwise, we pass no instance to create a
    new object, since self.obj is None if no ID is provided.
    '''
    def get(self, request, module_id, model_name, id = None):
        form = self.get_form(self.model, instance = self.obj)
        return self.render_to_response({'form' : form, 'object' : self.obj})

    '''
    If the form is valid, we create a new object and
    assign request.user as its owner before saving it to the
    database. We check for the id parameter. If no ID is
    provided, we know the user is creating a new object instead
    of updating an existing one. If this is a new object, we create
    a Content object for the given module and associate the new
    content to it.
    '''
    def post(self, request, module_id, model_name, id = None):
        form = self.get_form(self.model, instance = self.obj, data = request.POST, files = request.FILES)
        if form.is_valid():
            obj = form.save(commit = False)
            obj.owner = request.user
            obj.save()
            if not id:
                #new Content object
                Content.objects.create(module = self.module, item = obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form' : form, 'object' : self.obj})

class ContentDeleteView(View):

    def post(self, request, id):
        content = get_object_or_404(Content, id = id, module__course__owner = request.user)
        module = content.module
        #delete related Text, Video, Image or File object
        content.item.delete()
        #delete Content object
        content.delete()
        return redirect('module_content_list', module.id)

class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module, id = module_id, course__owner = request.user)
        return self.render_to_response({'module' : module})

'''
CsrfExemptMixin: To avoid checking the CSRF token in the POST
requests. We need this to perform AJAX POST requests
without having to generate a csrf_token .
JsonRequestResponseMixin: Parses the request data as JSON and
also serializes the response as JSON and returns an HTTP
response with the application/json content type.
'''
class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id = id, course__owner = request.user).update(order = order)
        return self.render_json_response({'saved' : 'OK'})

class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id = id, module__course__owner = request.user).update(order = order)
        return self.render_json_response({'saved' : 'OK'})

'''
Mixins are a special kind of multiple inheritance for a class. You can
use them to provide common discrete functionality that, added to
other mixins, allows you to define the behavior of a class. There are
two main situations to use mixins:
1) You want to provide multiple optional features for a class
2) You want to use a particular feature in several classes
'''

'''
Django comes with an abstraction layer to work with multiple forms
on the same page. These groups of forms are known as formsets.
Formsets manage multiple instances of a certain Form or ModelForm . All
forms are submitted at once and the formset takes care of the initial
number of forms to display, limiting the maximum number of
forms that can be submitted and validating all the forms.
'''

'''
TemplateResponseMixin: This mixin takes charge of rendering
templates and returning an HTTP response. It requires a
template_name attribute that indicates the template to be
rendered and provides the render_to_response() method to pass
it a context and render the template.
'''