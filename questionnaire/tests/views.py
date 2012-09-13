
from questionnaire.models import Question,Questionnaire,QuestionAnswer, AnswerSet, QuestionGroup
from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from django.core.urlresolvers import reverse



        
        
class DoQuestionnaireTests(TestCase):
    fixtures = ['test_questionnaire_fixtures.json']
    '''
        This class will house unit test for the do_questionnaire view function in the views module of the questionnaire package
    '''
    def setUp(self):
        
        """
            We need to have some intitial data
            1. A User we can login with
            2. A Questionnaire defined, which has 2 QuestionGroup defined, each with 1 question of each question type
        """
        testquestionnaire = Questionnaire.objects.get(pk=1)      
        testquestiongroup=QuestionGroup.objects.get(pk=1)
        self.client = Client()
        self.user_test = User.objects.create_user('user', 'email@email.com', 'password')          
        self.answerset = AnswerSet.objects.create(user=self.user_test,questionnaire=testquestionnaire,questiongroup=testquestiongroup)

   
  
    def test_no_user(self):
        """
            A get request to this view without a logged in user should redirect to the default login url
        """
        
        url = reverse('handle_next_questiongroup_form', kwargs={'questionnaire_id':1, 'order_index':1})
        response = self.client.get(url)
        self.assertEquals (302, response.status_code )
        self.assertEquals (response['Location'], 'http://testserver/accounts/login/?next=%s' % url )
        
    def test_get_valid_questionnaire_firsttime(self):
        """
            A GET request to the ''handle_next_questiongroup_form'' view specifying a valid questionnaire id,
            which the user hasn't participated in yet should:
            1. yield a http 200 response
            2. use the questionform.html template
            3. have a form in the context containing fields representing the first group in the questionnaire
            but unbound to any data (ie. not have any value associated with them)
        """        
        
        self.client.login(username='user', password='password') 
        url = reverse('handle_next_questiongroup_form', kwargs={'questionnaire_id':1, 'order_index':0})   
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200, 'user authenticated and can access the page')
        self.assertTemplateUsed('questionform.html') 
        
        
        form = resp.context['form']
        
        
       
        
        
        expected = [    ('Q1 G1 Charfield','charfield'),
                        ('Q2 G1 Textfield','textfield'),
                        ('Q3 G1 boolean','booleanfield'),]
        
        
        for index in range(len(form.base_fields)):
            
            self.assertEqual(form.base_fields.value_for_index(index).label, expected[index][0])
            
        
        
    def test_get_invalid_questionnaire(self):
        """
            A GET request to the ''handle_next_questiongroup_form'' view specifying a invalid questionnaire id
            should yield a http 404 response as this questionnaire does not exist
        """
        
        self.client.login(username='user', password='password') 
        url = reverse('handle_next_questiongroup_form', kwargs={'questionnaire_id': 2, 'order_index':0})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404, 'There are no questionnaire with id 2!')
        
    def test_get_invalid_order_info(self):
        """
            A GET request to the ''handle_next_questiongroup_form'' view specifying a invalid questionnaire id
            should yield a http 404 response as this questionnaire does not exist
        """
        
        self.client.login(username='user', password='password') 
        url = reverse('handle_next_questiongroup_form', kwargs={'questionnaire_id': 2, 'order_index':10})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404, 'There are no questionnaire with id 2!')
        
        
    def test_post_success_firsttime(self):
        """
            A POST request to the ''handle_next_questiongroup_form'' view specifying a valid questionnaire id and no
            question group id, where this is the first time a user has attempted the questionnaire should:
            1. Create a new AnswerSet related to the User and the Questionnaire specified
            2. It should create a QuestionAnswer object for each question, related to the AnswerSet by a fk relationship
            3. It should redirect to the handle_next_questiongroup_form url specifying the questionnaire id and the 
            id of the next question group for the questionniare (in this case there is one as that is how we setup the fixture)
        """
        #create a new user so that we know that this is the firsttime that the user has answered the questionniare

        
        self.client.login(username='user', password='password')
        url = reverse('handle_next_questiongroup_form', kwargs={'questionnaire_id':1})
        post_data =  {u'1': [u'a'], u'2': [u'a'], u'3': 1}
        resp = self.client.post(url,post_data)        
        self.assertEqual(302, resp.status_code)      
        self.assertEqual(resp['Location'], 'http://testserver/questionnaire/qs/1/1/')
        
        
        test_question = Question.objects.get(pk=1)
        test_questionnaire = Questionnaire.objects.get(pk=1)
        test_question_group = test_questionnaire.get_group_for_index(0)[0]
        test_answer_Set = AnswerSet.objects.get(user=self.user_test, 
                                                questionnaire=test_questionnaire,
                                                questiongroup=test_question_group )
        self.assertEqual(test_answer_Set.user, self.user_test)
        self.assertEqual(QuestionAnswer.objects.get(question=test_question, answer_set=test_answer_Set).answer, 'a')

        
    def test_post_success_lastgroup(self):
        """
            A POST request to the ''handle_next_questiongroup_form'' view specifying a valid questionnaire id and the id
            of the last QuestionGroup id, where the user has already answered at least one other QuestionGroups should
            1. NOT create a new AnswerSet, it should use the existing AnswerSet
            2. It should create a QuestionAnswer object for each question, related to the AnswerSet by a fk relationship
            3. It should redirect to the finish url.
        """
        self.client.login(username='user', password='password')        
        url = reverse('handle_next_questiongroup_form', kwargs={'questionnaire_id': 1, 'order_index': 1})
        post_data =  {u'4': [u'Dropdown 1'], u'5': [u'Radio 1'], u'6': [u'MultipleChoice 1']}
        resp = self.client.post(url,post_data)     
        self.assertEqual(resp.status_code, 302)     
        self.assertEqual(resp['Location'], 'http://testserver/questionnaire/finish/')
        
    def test_post_success_retry(self):
        """
            In this scenario the user has already completed the first group in the questionnaire, but is retrying/editing their response
            A valid post request will:
            1. NOT create a new AnswerSet
            2. Will create new QuestionAnswer objects only for those questions that have changed, but not for answers which are the same
            (these objects should remain unchanged)
            3. It should redirect to the handle_next_questiongroup_form url specifying the questionnaire id and the 
            id of the next question group for the questionniare (in this case there is one as that is how we setup the fixture)
        """
        
        '''
        create object first, to simulate it is already answered! and then try to post the question id but different answer!
        '''
        self.question_answer_1 = QuestionAnswer.objects.create(question=Question.objects.get(pk=1),answer="charfield",answer_set=AnswerSet.objects.get(pk=1))
        self.question_answer_2 = QuestionAnswer.objects.create(question=Question.objects.get(pk=2),answer="textfield",answer_set=AnswerSet.objects.get(pk=1))
        self.question_answer_3 = QuestionAnswer.objects.create(question=Question.objects.get(pk=3),answer="True",answer_set=AnswerSet.objects.get(pk=1))  
        
        self.client.login(username='user', password='password')
        url = reverse('handle_next_questiongroup_form', kwargs={'questionnaire_id': 1, 'order_index':0})
        post_data =  {u'1': [u'b'], u'2': [u'b'], u'3': 1}
        resp = self.client.post(url,post_data)


        self.assertEqual(302, resp.status_code)      
        self.assertEqual(resp['Location'], 'http://testserver/questionnaire/qs/1/1/')
        
        '''
        Check if the new post creates a new object and compare it is not the same answer as the previous one and check the count of the questionanswer
        increased by 2 meaning a new object is made
        '''
        self.assertEqual(QuestionAnswer.objects.get(pk=1).answer, 'charfield')
        self.assertEqual(QuestionAnswer.objects.get(pk=4).answer, 'b')                
        self.assertNotEqual(QuestionAnswer.objects.get(pk=4).answer, QuestionAnswer.objects.get(pk=1).answer) 
        
        
        '''
        check if there are only 1 AnswerSet object created which means there is no extra AnswerSet object created
        '''               
        self.assertEqual(AnswerSet.objects.get(pk=1).user, User.objects.get(username='user'))
        self.assertEqual(AnswerSet.objects.all().count(), 1 )
        
    def test_post_failure(self):
        
        """
            An invalid POST request to the ''do_questionnaire'' view specifying a valid questionnaire id 
            where this is the first request made on a quesstionnaire that the user has not previously attempted should:
            1. Not create an Answerset, or any QuestionAnswer objects
            2. Should redisplay the original form, with appropriate error messages
        
        """
        
        self.client.login(username='user', password='password')
        post_data =  {u'1': [u'c'], u'2': [u'b'], u'3': [u'xxx']}
        
        resp = self.client.post('/questionnaire/qs/1/',post_data)
        self.assertEqual(200, resp.status_code)
        self.assertTrue(len(resp.context['form'].errors) > 0)
        
    def test_get_success_name_provided_and_in_request(self):
        '''
            If the success name argument is passed to the view, and there is data for it in the get request
            then when the form is rendered there should be a hidden input with id the same as the success name,
            and the value being equal to the data passed into the request
        '''
        self.client.login(username='user', password='password')
        url = reverse('do_questionnaire_with_success', kwargs={'questionnaire_id': 1})
        resp = self.client.get(url, data={'on_success':reverse('questionnaire_finish')})
        
        self.assertTrue('on_success' in resp.context['form'].fields)
        self.assertEqual(resp.context['form'].initial['on_success'], reverse('questionnaire_finish'))
    
    def test_get_success_name_provided_and_not_in_request(self): 
        '''
            If the success name argument is passed to the view, and there is NOT data for it in the get request
            then there shouldn't be any hidden fields in the form
        '''
        self.client.login(username='user', password='password')
        url = reverse('do_questionnaire_with_success', kwargs={'questionnaire_id': 1})
        resp = self.client.get(url)
        
        self.assertFalse('on_success' in resp.context['form'].fields)
        self.assertFalse('on_success' in resp.context['form'].initial)
    
    def test_post_success_name_provided_and_in_post_firstgroup(self):
        '''
            If there is a valid post that is passed in a request to the view that defines a
            success name parameter (defined in the url config), and in this post there is data for this success name,
            AND there are more groups to be completed in the questionnaire, then:
            1. Nothing should be saved for this extra post parameter (its not a question!!!)
            2. The redirect url should be a get request that contains the success_name data
        ''' 
        
        self.client.login(username='user', password='password')
        url = reverse('do_questionnaire_with_success', kwargs={'questionnaire_id':1})
        post_data =  {u'1': [u'a'], u'2': [u'a'], u'3': 1, 'on_success':reverse('questionnaire_finish')}
        resp = self.client.post(url,post_data)        
        
        test_questionnaire = Questionnaire.objects.get(pk=1)
        test_question_group = test_questionnaire.get_group_for_index(0)[0]
        test_answer_set = AnswerSet.objects.get(user=self.user_test, 
                                                questionnaire=test_questionnaire,
                                                questiongroup=test_question_group )
        
        self.assertEqual(len(test_answer_set.questionanswer_set.all()), 3)
        
        self.assertEqual(302, resp.status_code)      
        redirect_url = reverse('do_questionnaire_with_success', kwargs={'questionnaire_id':1 , 'order_index':1})
        self.assertEqual(resp['Location'], 'http://testserver%s?on_success=%s' % (redirect_url, reverse('questionnaire_finish')))
    
        
    def test_post_success_name_provided_and_in_post_lastgroup(self):
        '''
            If there is a valid post that is passed in a request to the view that defines a
            success name parameter(defined in the url config), and in this post there is data for this success name,
            AND there are NO more groups to be completed in the questionnaire, then:
            1. Nothing should be saved for this extra post parameter (its not a question!!!)
            2. The redirect url should be a get request to the url specified in this success_name data
        ''' 
        self.client.login(username='user', password='password')
        url = reverse('do_questionnaire_with_success', kwargs={'questionnaire_id':1, 'order_index':1})
        post_data =  {u'4': [u'Dropdown 1'], u'5': [u'Radio 1'], u'6': [u'MultipleChoice 1'], 'on_success':reverse('questionnaire_finish')}
        resp = self.client.post(url,post_data)        
        
        
        test_questionnaire = Questionnaire.objects.get(pk=1)
        test_question_group = test_questionnaire.get_group_for_index(1)[0]
        test_answer_set = AnswerSet.objects.get(user=self.user_test, 
                                                questionnaire=test_questionnaire,
                                                questiongroup=test_question_group )
        
        self.assertEqual(len(test_answer_set.questionanswer_set.all()), 3)
        self.assertRedirects(resp, reverse('questionnaire_finish'))
        
    def test_valid_post_with_limit_of_one(self): 
        '''
            A group limit of 1 means that you only want to do one group: the group that you are requesting in the
            order_index.
            If a group limit of one is passed in, and the questionnaire contains more than one
            questiongroup after the group being requested, then a valid post will cause a redirect to the 
            finish_url, and not to the next questiongroup as would be the case for a limit of 0 or more than 1
        '''
        test_questionnaire = Questionnaire.objects.create(name='test_questionnaire')
        test_group = QuestionGroup.objects.get(pk=1) #we know that this is in the db from the fixture
        
        for index in range(3): #add the same group thrice
            test_questionnaire.add_question_group(test_group)
            
        self.client.login(username='user', password='password')
        
        url = reverse('handle_next_questiongroup_form', kwargs={'questionnaire_id': 1, 'order_index':0, 'group_limit':1})
        post_data =  {u'1': [u'b'], u'2': [u'b'], u'3': 1} #a valid post for this questiongroup
        resp = self.client.post(url,post_data)

        self.assertEqual(resp.status_code, 302)     
        self.assertEqual(resp['Location'], 'http://testserver/questionnaire/finish/')#this is what is configured as the finish url in the url conf

        
    def test_valid_post_with_limit_of_greater_than_one_groups_avaialble(self):
        '''
            A group limit of more than one means that you want to do the current group (defined by order_index)
            and then (group_index -1) more groups (if there are that many in the sequence).
            
            In this case there are groups available to fulfill this request. for example there are three
            groups, and we are requesting the first group with a group_limit of 2, in this case
            a valid post to the url will decrement the current group_limit when it redirects to the url
            for the next group (Eventually it will hit 1 and then that will be the last group carried out)
        '''
        
        self.assertTrue(False)
        
    def test_valid_post_with_limit_of_greater_than_one_groups_not_avaialble(self):
        '''
            A group limit of more than one means that you want to do the current group (defined by order_index)
            and then (group_index -1) more groups (if there are that many in the sequence).
            
            In this case there are not enough groups to fulfill this request for example there
            are 3 groups and we are requesting group 2 with a group limit of 3. IN this case the questionnaire
            will simply terminate as usual after the last group.
        '''
        
        self.assertTrue(False)
        
        
        
class QuestionnaireViewTests(TestCase):
    fixtures = ['test_questionnaire_fixtures.json']
    '''
        This class will house unit test for the questionnaire package
        
        The views under test are:
        
        handle_next_questiongroup_form
        finish
        display_question_answer
        
        
        
        @author: jjm20
    '''
    def setUp(self):
        
        """
            We need to have some intitial data
            1. A User we can login with
            2. A Questionnaire defined, which has 2 QuestionGroup defined, each with 1 question of each question type
        """
        testquestionnaire = Questionnaire.objects.get(pk=1)      
        testquestiongroup=QuestionGroup.objects.get(pk=1)
        self.client = Client()
        self.user_test = User.objects.create_user('user', 'email@email.com', 'password')          
        self.answerset = AnswerSet.objects.create(user=self.user_test,questionnaire=testquestionnaire,questiongroup=testquestiongroup)

        
        super(QuestionnaireViewTests,self).setUp()
                 
    def test_finish_view(self):
        
        """
            A GET request to the ''finish'' view should :
            1. return a 200 HTTPResponse
            2. Render the finish.html template
        """
        url = reverse('questionnaire_finish')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200, 'finish page should be shown')
        self.assertTemplateUsed('finish.html') 
        
    def test_display_question_answer_invalid_questionnaire(self):
        """
            GET request to ''display_question_answer'' with an invalid question id (ie it doesn't exist)(but logged in) should:
            1. yield a http 404 response
        """
        '''
        This test will fail because the view for display_questionnaire have not been fully implemented to use questionnaire_id to call each of the
        question group.
        i.e. still using objects.get.all() - this however will pass if the actual view code have been implemented
        '''
        self.client.login(username='user', password='password') 
        url = reverse('display_question_answer', kwargs={'questionnaire_id':2 , 'questiongroup_id': 1})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404, 'There are no questionnaire with id 2!')
        
        
    def test_display_question_answer_valid_questionnaire_not_logged_in(self):
        """
            GET request to ''display_question_answer'' without being logged in should:
            1. redirect to the default login url
        """
        url = reverse('display_question_answer', kwargs={'questionnaire_id':1, 'questiongroup_id': 1})
        response = self.client.get(url)
        self.assertEquals (302, response.status_code)
        
        
    def test_display_question_answer_valid_questionnaire_not_answered(self):
        """
            GET request to ''display_question_answer'' with a logged in user and a valid question id but one that has not been answered
            should :
            1. return http 200 response
            2. template used should be questionAnswer.html
            3. context should not contain any answers (which will cause the template to show that you have no answers)
        """
        self.client.login(username='user', password='password')
        url = reverse('display_question_answer', kwargs={'questionnaire_id':1, 'questiongroup_id' : 1})    
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200, 'user authenticated and can access the page')
        self.assertTemplateUsed('questionanswer.html')         
        self.assertEqual(len(resp.context['questionanswer']), 0)
        

        
        
    def test_display_question_answer_valid_questionnaire_partialy_answered(self):
        """
            GET request to ''display_question_answer'' with a logged in user and a valid question id for a questionnaire that
            has been partially answered should:
            1. return htt 200 response
            2. template used should be questionAnswer.html
            3. context should contain the answers in such2 a way that can be rendered by their group
            4. Any unanswered questions should show that they haven't yet been answered
        """
        self.question_answer_1 = QuestionAnswer.objects.create(question=Question.objects.get(pk=1),answer="charfield",answer_set=AnswerSet.objects.get(pk=1))
        self.question_answer_2 = QuestionAnswer.objects.create(question=Question.objects.get(pk=2),answer="textfield",answer_set=AnswerSet.objects.get(pk=1))
        self.question_answer_3 = QuestionAnswer.objects.create(question=Question.objects.get(pk=3),answer="True",answer_set=AnswerSet.objects.get(pk=1))

        self.client.login(username='user', password='password')
        url = reverse('display_question_answer', kwargs={'questionnaire_id':1 , 'questiongroup_id':1})    
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200, 'user authenticated and can access the page')
        self.assertTemplateUsed('questionanswer.html') 
        self.assertLess(len(resp.context['questionanswer']), 6)
        self.assertEqual(len(resp.context['questionanswer']), 3)
        
        
    def test_display_question_answer_valid_questionnaire_fully_answered(self):
        """
            GET request to ''display_question_answer'' with a logged in user and a valid question id for a questionnaire that
            has been partially answered should:
            1. return htt 200 response
            2. template used should be questionAnswer.html
            3. context should contain the answers in such a way that can be rendered by their group
        """
        self.question_answer_1 = QuestionAnswer.objects.create(question=Question.objects.get(pk=1),answer="charfield",answer_set=AnswerSet.objects.get(pk=1))
        self.question_answer_2 = QuestionAnswer.objects.create(question=Question.objects.get(pk=2),answer="textfield",answer_set=AnswerSet.objects.get(pk=1))
        self.question_answer_3 = QuestionAnswer.objects.create(question=Question.objects.get(pk=3),answer="True",answer_set=AnswerSet.objects.get(pk=1))
        self.question_answer_4 = QuestionAnswer.objects.create(question=Question.objects.get(pk=4),answer="Radio 1",answer_set=AnswerSet.objects.get(pk=1))
        self.question_answer_5 = QuestionAnswer.objects.create(question=Question.objects.get(pk=5),answer="Drop 1",answer_set=AnswerSet.objects.get(pk=1))
        self.question_answer_6 = QuestionAnswer.objects.create(question=Question.objects.get(pk=6),answer="[u'Multiple Choice 1']",answer_set=AnswerSet.objects.get(pk=1))
        
        
        self.client.login(username='user', password='password')
        url = reverse('display_question_answer', kwargs={'questionnaire_id':1, 'questiongroup_id':1})            
        resp = self.client.get(url)        
        self.assertEqual(resp.status_code, 200, 'user authenticated and can access the page')
        self.assertTemplateUsed('display_questionanswer.html')    
         
        self.assertEqual(len(resp.context['questionanswer']), 6)
        

        
                
    def test_display_question_answer_valid_questionnaire_edited_answers(self):
        """
            GET request to ''display_question_answer'' with a logged in user and a valid question id for a questionnaire that
            has been partially answered should:
            1. return htt 200 response
            2. template used should be questionAnswer.html
            3. context should contain the answers in such a way that can be rendered by their group
            4. Where the answers have been edited (i.e. there are more than one QuestionAnswer for this questionnaire) only the
            most recent answer should be shown.
        """
        self.question_answer_1 = QuestionAnswer.objects.create(question=Question.objects.get(pk=1),answer="charfield",answer_set=AnswerSet.objects.get(pk=1))
        self.question_answer_2 = QuestionAnswer.objects.create(question=Question.objects.get(pk=2),answer="textfield",answer_set=AnswerSet.objects.get(pk=1))
        self.question_answer_3 = QuestionAnswer.objects.create(question=Question.objects.get(pk=3),answer="True",answer_set=AnswerSet.objects.get(pk=1))
        self.question_answer_7 = QuestionAnswer.objects.create(question=Question.objects.get(pk=3),answer="False",answer_set=AnswerSet.objects.get(pk=1))
        
        
        
        
        self.client.login(username='user', password='password')
        url = reverse('display_question_answer', kwargs={'questionnaire_id':1 , 'questiongroup_id': 1})    
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200, 'user authenticated and can access the page')
        self.assertTemplateUsed('edit_questionanswer_form.html') 
 
        self.assertEqual(len(resp.context['questionanswer']), 3)
        
    def test_edit_question_answer_no_user(self):
        
        '''
            A get request to this view without a logged in user should redirect to the default login url
        '''
        
        url = reverse('edit_question_answer', kwargs={'questionnaire_id':1, 'order_index':1})
        response = self.client.get(url)
        self.assertEquals (302, response.status_code )
        self.assertEquals (response['Location'], 'http://testserver/accounts/login/?next=%s' % url )   
        
    
    def test_edit_question_answer_first_group_submit(self):
        """
            A GET request to the ''edit_question_answer'' view specifying a valid questionnaire id,
            which the user has already got answers for should:
            1. yield a http 200 response
            2. use the questionform.html template
            3. have a form in the context containing fields representing the first group in the questionnaire
            but Bound to any data (ie. Have data initialize and bound to them!)
            4. After form submission, it goes to the next questiongroup
        """        
        self.question_answer_1 = QuestionAnswer.objects.create(question=Question.objects.get(pk=1),answer="charfield_answer",answer_set=self.answerset)
        self.question_answer_2 = QuestionAnswer.objects.create(question=Question.objects.get(pk=2),answer="textfield_answer",answer_set=self.answerset)
        self.question_answer_3 = QuestionAnswer.objects.create(question=Question.objects.get(pk=3),answer="True",answer_set=self.answerset)

          
        
        self.client.login(username='user', password='password') 
        url = reverse('edit_question_answer', kwargs={'questionnaire_id':1, 'order_index':0})   
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200, 'user authenticated and can access the page')
        self.assertTemplateUsed('edit_questionanswer_form.html') 
        
        
        form = resp.context['form']
        

        expected = [    ('Q1 G1 Charfield','charfield_answer'),
                        ('Q2 G1 Textfield','textfield_answer'),
                        ('Q3 G1 boolean',True),]
        
        
        for index in range(len(form.base_fields)):
            
            self.assertEqual(form.base_fields.value_for_index(index).label, expected[index][0])
            self.assertEqual(form.base_fields.value_for_index(index).initial, expected[index][1])
            
         
        '''
        Adds 3 more answer for questiongroup 2
        '''
            
        self.answerset = AnswerSet.objects.create(user=self.user_test,questionnaire=Questionnaire.objects.get(pk=1),
                                                  questiongroup=QuestionGroup.objects.get(pk=2))
        self.question_answer_4 = QuestionAnswer.objects.create(question=Question.objects.get(pk=4),answer="Dropdown 3",answer_set=self.answerset)
        self.question_answer_5 = QuestionAnswer.objects.create(question=Question.objects.get(pk=5),answer="Radio 3",answer_set=self.answerset)
        self.question_answer_6 = QuestionAnswer.objects.create(question=Question.objects.get(pk=6),answer="MultipleChoice 3",answer_set=self.answerset)
        

        post_data =  {u'4': u'Dropdown 1', u'5': u'Radio 1', u'6': u'MultipleChoice 1'}
        url_2 = reverse('edit_question_answer', kwargs={'questionnaire_id':1, 'order_index':1})   
        resp_2 = self.client.post(url_2,post_data)
        
        self.assertEqual(302, resp_2.status_code)   
           
        self.assertEqual(resp_2['Location'], 'http://testserver/questionnaire/finish/')

         
    def test_all_question_answers_for_questiongroup(self):
        """
            A GET request to the ''all_question_answers_for_questiongroup'' view specifying a valid questionnaire id,
            which the user hasn't participated in yet should:
            1. yield a http 200 response
            2. use the questionform.html template
            3. Since its showing all of the answer for a questiongroup, it is expected the number of answer is more than one for each question

        """        
        self.question_answer_1 = QuestionAnswer.objects.create(question=Question.objects.get(pk=1),answer="charfield_answer",answer_set=AnswerSet.objects.get(pk=1))
        self.question_answer_2 = QuestionAnswer.objects.create(question=Question.objects.get(pk=2),answer="textfield_answer",answer_set=AnswerSet.objects.get(pk=1))
        self.question_answer_3 = QuestionAnswer.objects.create(question=Question.objects.get(pk=3),answer="True",answer_set=AnswerSet.objects.get(pk=1))
        
          
        
        self.client.login(username='user', password='password') 
        url = reverse('all_question_answers_for_questiongroup', kwargs={'user_id':self.user_test.id,'questionnaire_id':1, 'questiongroup_id':1})   
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200, 'user authenticated and can access the page')
        self.assertTemplateUsed('all_questionanswers.html') 
        self.assertEqual(len(resp.context['questionanswer_list']), 3)
        
        
    def test_questionnaire_detail_list(self):
        """
            A GET request to the ''questionnaire_detail_list'' view specifying a valid questionnaire id,
            which the user hasn't participated in yet should:
            1. yield a http 200 response
            2. use the questionform.html template

        """        
        self.question_answer_1 = QuestionAnswer.objects.create(question=Question.objects.get(pk=1),answer="charfield_answer",answer_set=AnswerSet.objects.get(pk=1))
        self.question_answer_2 = QuestionAnswer.objects.create(question=Question.objects.get(pk=2),answer="textfield_answer",answer_set=AnswerSet.objects.get(pk=1))
        self.question_answer_3 = QuestionAnswer.objects.create(question=Question.objects.get(pk=3),answer="True",answer_set=AnswerSet.objects.get(pk=1))

        
        self.client.login(username='user', password='password') 
        url = reverse('questionnaire_detail_list', kwargs={'questionnaire_id':1})   
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200, 'user authenticated and can access the page')
        self.assertTemplateUsed('questionnaire_detail.html')         
        self.assertEqual(len(resp.context['groups_list']), 2)
        
        