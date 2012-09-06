from django.conf.urls import url, patterns
from django.views.generic.simple import direct_to_template




urlpatterns = patterns('questionnaire.views',
        
        #url(r'^/$', view = '<view_name>',name = 'a_name'),              
          url (r'^$', 
               view= 'questionnaire_index',
               name='questionnaire_index'),
                
                       
          url(r'^qs/(?P<questionnaire_id>\d+)/(?P<order_info>\d+)/$', 
          view = 'do_questionnaire',
          name = 'handle_next_questiongroup_form'),                      
    
          url(r'^qs/(?P<questionnaire_id>\d+)/$', 
          view = 'do_questionnaire',
          name = 'handle_next_questiongroup_form'), 
                       
        url(r'^finish/$', 
            view = 'finish',
            name = 'questionnaire_finish'),   
    
        
        url(r'^questionanswer/(?P<questionnaire_id>\d+)/(?P<questiongroup_id>\d+)/$', 
            view = 'display_question_answer',
            name = 'display_question_answer'),
                       
        url(r'^edit/(?P<questionnaire_id>\d+)/(?P<order_info>\d+)/$', 
            view = 'do_questionnaire',
            name = 'edit_question_answer'),
         
        url(r'^trailquestionanswers/(?P<user_id>\d+)/(?P<questionnaire_id>\d+)/(?P<questiongroup_id>\d+)/$', 
            view = 'all_question_answers_for_questiongroup',
            name = 'all_question_answers_for_questiongroup'),
                       
        url(r'^(?P<questionnaire_id>\d+)/$', 
            view = 'questionnaire_detail_list',
            name = 'questionnaire_detail_list'),
                             
    
)
