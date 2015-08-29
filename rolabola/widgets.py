from django.forms import Select
from social import settings
from django.template.loader import render_to_string
from django.utils.safestring import *

class SelectOrCreate(Select):
    """
    Base class for all <select> widgets with chosen js.
    https://djangosnippets.org/snippets/3032/
    """
    def __init__(self, form, url, attrs=None, choices=(), ):
      super(SelectOrCreate, self).__init__(attrs, choices)
      self.form = form
      self.url = url

    def render(self, name, value, attrs=None, choices=()):
      output = [super(SelectOrCreate, self).render(name, value, attrs, choices), ]
      final_attrs = self.build_attrs(attrs, name=name)
      ret = {'final_attrs': final_attrs,
             'STATIC_URL': settings.STATIC_URL,
             'id': final_attrs['id'],
             'form': self.form,
             'redirect_url': self.url}
      output.append(mark_safe(render_to_string('widgets/select_or_create.html', ret)))
      return mark_safe('\n'.join(output))
