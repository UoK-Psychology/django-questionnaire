from django.conf.urls import url, patterns
from django.core.urlresolvers import reverse




urlpatterns = patterns('questionnaire.views',
        
        #url(r'^/$', view = '<view_name>',name = 'a_name'),              
          url (r'^$', 
               view= 'questionnaire_index',
               name='questionnaire_index',
               kwargs={'template_name':'questionnaire/questionnaire_index.html'}),
                
                       
          url(r'^qs/(?P<questionnaire_id>\d+)/(?P<order_index>\d+)/$', 
          view = 'do_questionnaire',
          name = 'handle_next_questiongroup_form',
          kwargs={'template_name':'questionnaire/questionform.html',
                  'next_form_name':'handle_next_questiongroup_form',
                    'finished_url':'/questionnaire/finish/'},),
        
    
          url(r'^qs/(?P<questionnaire_id>\d+)/$', 
          view = 'do_questionnaire',
          name = 'handle_next_questiongroup_form',
          kwargs={'template_name':'questionnaire/questionform.html',
                  'next_form_name':'handle_next_questiongroup_form',
                    'finished_url':'/questionnaire/finish/'},), 
                       
        url(r'^finish/$', 
            view = 'finish',
            name = 'questionnaire_finish',
            kwargs={'template_name':'questionnaire/finish.html'},),   
    
        
        url(r'^questionanswer/(?P<questionnaire_id>\d+)/(?P<questiongroup_id>\d+)/$', 
            view = 'display_question_answer',
            name = 'display_question_answer',
            kwargs={'template_name':'questionnaire/display_questionanswer.html'},),
                       
        url(r'^edit/(?P<questionnaire_id>\d+)/(?P<order_index>\d+)/$', 
            view = 'do_questionnaire',
            name = 'edit_question_answer',
            kwargs={'template_name':'questionnaire/questionform.html',
                    'next_form_name':'handle_next_questiongroup_form',
                    'finished_url':'/questionnaire/finish/'},),
         
        url(r'^trailquestionanswers/(?P<user_id>\d+)/(?P<questionnaire_id>\d+)/(?P<questiongroup_id>\d+)/$', 
            view = 'all_question_answers_for_questiongroup',
            name = 'all_question_answers_for_questiongroup',
            kwargs={'template_name':'questionnaire/all_questionanswers.html'},),
                       
        url(r'^(?P<questionnaire_id>\d+)/$', 
            view = 'questionnaire_detail_list',
            name = 'questionnaire_detail_list',
            kwargs={'template_name':'questionnaire/questionnaire_detail.html'},),
                             
    
)
