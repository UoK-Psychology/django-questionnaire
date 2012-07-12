from django.conf.urls import *
from views import *
from django.views.generic.simple import direct_to_template




urlpatterns = patterns('questionnaire.views',
        
        #url(r'^/$', view = '<view_name>',name = 'a_name'),              
          url (r'^$',
         direct_to_template,
          { 'template': 'a_template.html' }, 'index'

    ),
          url(r'^qs/(?P<questionnaire_id>\d+)/(?P<order_info>\d+)/$', 
          view = 'get_next_questiongroup',
          name = 'get_next_questiongroup'),
        
          url(r'^qs/(?P<questionnaire_id>\d+)/$', 
          view = 'get_next_questiongroup',
          name = 'get_next_questiongroup'),
                       
        url(r'^finish/$', 
            view = 'finish',
            name = 'questionaire_finish'),   
    
)
