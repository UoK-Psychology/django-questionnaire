from django.conf.urls import url, patterns




urlpatterns = patterns('questionnaire.views',
        
        #url(r'^/$', view = '<view_name>',name = 'a_name'),              
          url (r'^$', 
               view= 'questionnaire_index',
               name='questionnaire_index',
               kwargs={'template':'questionnaire/questionnaire_index.html'}),
                
                       
          url(r'^qs/(?P<questionnaire_id>\d+)/(?P<order_index>\d+)/$', 
          view = 'do_questionnaire',
          name = 'handle_next_questiongroup_form',
          kwargs={'template':'questionnaire/questionform.html'},),
        
    
          url(r'^qs/(?P<questionnaire_id>\d+)/$', 
          view = 'do_questionnaire',
          name = 'handle_next_questiongroup_form',
          kwargs={'template':'questionnaire/questionform.html'},), 
                       
        url(r'^finish/$', 
            view = 'finish',
            name = 'questionnaire_finish',
            kwargs={'template':'questionnaire/finish.html'},),   
    
        
        url(r'^questionanswer/(?P<questionnaire_id>\d+)/(?P<questiongroup_id>\d+)/$', 
            view = 'display_question_answer',
            name = 'display_question_answer',
            kwargs={'template':'questionnaire/display_questionanswer.html'},),
                       
        url(r'^edit/(?P<questionnaire_id>\d+)/(?P<order_index>\d+)/$', 
            view = 'do_questionnaire',
            name = 'edit_question_answer',
            kwargs={'template':'questionnaire/questionform.html'},),
         
        url(r'^trailquestionanswers/(?P<user_id>\d+)/(?P<questionnaire_id>\d+)/(?P<questiongroup_id>\d+)/$', 
            view = 'all_question_answers_for_questiongroup',
            name = 'all_question_answers_for_questiongroup',
            kwargs={'template':'questionnaire/all_questionanswers.html'},),
                       
        url(r'^(?P<questionnaire_id>\d+)/$', 
            view = 'questionnaire_detail_list',
            name = 'questionnaire_detail_list',
            kwargs={'template':'questionnaire/questionnaire_detail.html'},),
                             
    
)
