from django.conf.urls import *
from views import get_next_questiongroup,finish,index
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
            name = 'questionnaire_finish'),   
    
        
        url(r'^Answer/(?P<questionnaire_id>\d+)$', 
            view = 'display_question_answer',
            name = 'display_question_answer'),   
    
)
