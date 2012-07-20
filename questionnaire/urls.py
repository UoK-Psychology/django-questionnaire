from django.conf.urls import *
from views import handle_next_questiongroup_form,finish,index
from django.views.generic.simple import direct_to_template




urlpatterns = patterns('questionnaire.views',
        
        #url(r'^/$', view = '<view_name>',name = 'a_name'),              
          url (r'^$',
         direct_to_template,
          { 'template': 'a_template.html' }, 'index'

    ),
          url(r'^qs/(?P<questionnaire_id>\d+)/(?P<order_info>\d+)/$', 
          view = 'handle_next_questiongroup_form',
          name = 'handle_next_questiongroup_form'),
        
          url(r'^qs/(?P<questionnaire_id>\d+)/$', 
          view = 'handle_next_questiongroup_form',
          name = 'handle_first_questiongroup_form'),
                       
        url(r'^finish/$', 
            view = 'finish',
            name = 'questionnaire_finish'),   
    
        
        url(r'^Answer/(?P<questionnaire_id>\d+)$', 
            view = 'display_question_answer',
            name = 'display_question_answer'),   
    
)
