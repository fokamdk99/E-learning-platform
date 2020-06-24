from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField

# Create your models here.
class Subject(models.Model):
    title=models.CharField(max_length=200)
    slug=models.SlugField(max_length=200,unique=True)

    class Meta:
        ordering=['title']

    def __str__(self):
        return self.title

class Course(models.Model):
    owner=models.ForeignKey(User,related_name='courses_created',on_delete=models.CASCADE)
    subject=models.ForeignKey(Subject,related_name='courses',on_delete=models.CASCADE)
    title=models.CharField(max_length=200)
    slug=models.SlugField(max_length=200,unique=True)
    overview=models.TextField()
    created=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=['-created']

        def __str__(self):
            return self.title


class Module(models.Model):
    course=models.ForeignKey(Course,related_name='modules',on_delete=models.CASCADE)
    title=models.CharField(max_length=200)
    description=models.TextField(blank=True)
    order = OrderField(blank = True, for_fields = ['course'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return '{}. {}'.format(self.order, self.title)

class Content(models.Model):
    module = models.ForeignKey(Module,related_name='contents',on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    #ogranicz mozliwosc tworzenia contentu do podanych ponizej klas
    limit_choices_to = {'model__in':('text', 'video', 'image', 'file')}
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank = True, for_fields = ['module'])

    class Meta:
        ordering = ['order']
    '''
    Only the content_type and object_id fields have a corresponding column
    in the database table of this model. The item field allows you to
    retrieve or set the related object directly, and its functionality is
    built on top of the other two fields.
    '''

class ItemBase(models.Model):
    #generujemy automatyczny atrybut related_name, dzieki ktoremu kazda instancja bedzie nawiazywala 
    #do odpowiedniej klasy, czyli text_related, file_related, image_related albo video_related
    owner = models.ForeignKey(User, related_name='%(class)s_related', on_delete = models.CASCADE)
    title = models.CharField(max_length = 250)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

class Text(ItemBase):
    content = models.TextField()

class File(ItemBase):
    file = models.FileField(upload_to = 'files')

class Image(ItemBase):
    file = models.FileField(upload_to = 'images')

class Video(ItemBase):
    url = models.URLField()


'''
Django supports model inheritance. It works in a similar way to
standard class inheritance in Python. Django offers the following
three options to use model inheritance:
Abstract models: Useful when you want to put some
common information into several models. No database table
is created for the abstract model. (abstract = True)

Multi-table model inheritance: Applicable when each
model in the hierarchy is considered a complete model by
itself. A database table is created for each model.

Proxy models: Useful when you need to change the
behavior of a model, for example, by including additional
methods, changing the default manager, or using different
meta options. No database table is created for proxy models. (proxy = True)
'''