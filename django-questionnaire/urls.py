from django.conf.urls import *
from views import *
from django.views.generic.simple import direct_to_template




urlpatterns = patterns('django-questionnaire.views',
        
        #url(r'^/$', view = '<view_name>',name = 'a_name'),              
          url (r'^$',
         direct_to_template,
          { 'template': 'a_template.html' }, 'index'

    ),
                       
                       
    
)
