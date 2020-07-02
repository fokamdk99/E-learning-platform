from django import template

register = template.Library()


'''
We can apply it in templates as
object|model_name to get the model name for an object.
'''
@register.filter
def model_name(obj):
    try:
        return obj._meta.model_name
    except AttributeError:
        return None

'''
We want to know which type of object each of the item objects is: Text ,
Video , Image , or File . We need the model name to build the URL to edit
the object. Besides this, we could display each item in the template
differently, based on the type of content it is. We can get the model
for an object from the model's Meta class, by accessing the object's
_meta attribute. Nevertheless, Django doesn't allow accessing
variables or attributes starting with an underscore in templates to
prevent retrieving private attributes or calling private methods. We
can solve this by writing a custom template filter.
'''