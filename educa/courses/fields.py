from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class OrderField(models.PositiveIntegerField):
    def __init__(self, for_fields = None, *args, **kwargs):
        self.for_fields = for_fields
        super(OrderField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        #sprawdz czy dana instancja juz istnieje
        if getattr(model_instance, self.attname) is None:
            try:
                '''
                We build a QuerySet to retrieve all objects for the
                field's model. We retrieve the model class the field
                belongs to by accessing self.model .
                '''
                #tak jak np. User.objects.all()
                qs = self.model.objects.all()
                if self.for_fields:
                    #filter by objects with the same field values
                    #for field in "self.for_fields"
                    '''
                    We filter the QuerySet by the fields' current value for
                    the model fields that are defined in the for_fields
                    parameter of the field, if any. By doing so, we
                    calculate the order with respect to the given fields.
                    '''
                    query = {field:getattr(model_instance, field) for field in self.for_fields}
                    qs = qs.filter(**query)
                    '''na przykladzie modelu Module: tworzymy modul 'wprowadzenie do django', wiec najpierw
                    znajdujemy zadany kurs, do ktorego chcemy dodac modul (field:getattr(Module, 'course')),
                    a nastepnie wyszukujemy poprzez filtr wszystkie dotychczas utworzone moduly dla tego kursu
                    '''

                #get the order of the last item
                '''
                We retrieve the object with the highest order with
                from the database. If no
                object is found, we assume this object is the first one
                and assign the order 0 to it.
                '''
                last_item = qs.latest(self.attname)
                #If an object is found, we add 1 to the highest order found.
                value = last_item.order + 1
            except ObjectDoesNotExist:
                value = 0
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(OrderField, self).pre_save(model_instance, add)


'''
Field is an abstract class that represents a database table column.
In models, a field is instantiated as a class attribute and represents a particular table column.

It’s important to realize that a Django field class is not what is stored in your model attributes. 
The model attributes contain normal Python objects. The field classes you define in a model are 
actually stored in the Meta class when the model class is created. This is because the field 
classes aren’t necessary when you’re just creating and modifying attributes. Instead, they provide
the machinery for converting between the attribute value and what is stored in the database or 
sent to the serializer.

Keep this in mind when creating your own custom fields. The Django Field subclass you write 
provides the machinery for converting between your Python instances and the 
database/serializer values.

You will often end up creating two classes when you want a custom field:
The first class is the Python object that your users will manipulate. They will assign it to the 
model attribute, they will read from it for displaying purposes, things like that.
The second class is the Field subclass. This is the class that knows how to convert your first 
class back and forth between its permanent storage form and the Python form.

attrname: The attribute to use on the model object. This is the same as
"name", except in the case of ForeignKeys, where "_id" is appended.

name: The name of the field specified in the model.
'''