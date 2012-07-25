from questionnaire.views import *
from questionnaire.models import Question,Questionnaire,QuestionGroup,Question_order, QuestionGroup_order, AnswerSet
from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from django.core.urlresolvers import reverse


class OtherTests(TestCase):
    fixtures = ['test_questionnaire_fixtures.json',]
    
    def test(self):
        
        test_question = Question.objects.get(pk=3)
        self.assert_(test_question.label == 'test_question_booleanfield')
        
        
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
        
        self.client = Client()
        self.user_test = User.objects.create_user('user', 'email@email.com', 'password')
        testquestionnaire = Questionnaire.objects.get(pk=1)        
        self.answerset = AnswerSet.objects.create(user=self.user_test,questionnaire=testquestionnaire)
        super(QuestionnaireViewTests,self).setUp()
        
        
        
                                                                      

        
    
    def test_handle_next_questiongroup_form_no_user(self):
        
        """
            A get request to this view without a logged in user should redirect to the default login url
        """
        
        response = self.client.get('/questionnaire/qs/1/')
        self.assertEquals (302, response.status_code )
        
    def test_handle_next_questiongroup_form_get_valid_questionnaire_firsttime(self):
        """
            A GET request to the ''handle_next_questiongroup_form'' view specifying a valid questionnaire id,
            which the user hasn't participated in yet should:
            1. yield a http 200 response
            2. use the questionform.html template
            3. have a form in the context containing fields representing the first group in the questionnaire
            but unbound to any data (ie. not have any value associated with them)
        """        
        self.client.login(username='user', password='password')    
        resp = self.client.get('/questionnaire/qs/1/')
        self.assertEqual(resp.status_code, 200, 'user authenticated and can access the page')
        self.assertTemplateUsed('questionform.html') 
        
    def test_handle_next_questiongroup_form_get_valid_questionnaire_retry(self):
        """
            A GET request to the ''handle_next_questiongroup_form'' view specifying a valid questionnaire id,
            which the user has already reponsed to:
            1. yield a http 200 response
            2. use the questionform.html template
            3. have a form in the context containing fields representing the first group in the questionnaire
            but that is bound to the answers that were previously given by the user.
        """
        
        resp = self.client.get('/questionnaire/qs/1')
        self.assertEqual(resp.status_code, 200, 'first page should be shown')        
        self.assertTemplateUsed('questionform.html') 

        
    def test_handle_next_questiongroup_form_get_invalid_questionnaire(self):
        """
            A GET request to the ''handle_next_questiongroup_form'' view specifying a invalid questionnaire id
            should yield a http 404 response as this questionnaire does not exist
        """
        self.client.login(username='user', password='password') 
        resp = self.client.get('/questionnaire/qs/0/')
        self.assertEqual(resp.status_code, 404, 'There are no questionnaire with id 0!')
        
        
    def test_handle_next_questiongroup_form_post_success_firsttime(self):
        """
            A POST request to the ''handle_next_questiongroup_form'' view specifying a valid questionnaire id and no
            question group id, where this is the first time a user has attempted the questionnaire should:
            1. Create a new AnswerSet related to the User and the Questionnaire specified
            2. It should create a QuestionAnswer object for each question, related to the AnswerSet by a fk relationship
            3. It should redirect to the handle_next_questiongroup_form url specifying the questionnaire id and the 
            id of the next question group for the questionniare (in this case there is one as that is how we setup the fixture)
        """
        
        
        self.assert_(False, 'Not yet implemented')
        
    def test_handle_next_questiongroup_form_post_success_lastgroup(self):
        """
            A POST request to the ''handle_next_questiongroup_form'' view specifying a valid questionnaire id and the id
            of the last QuestionGroup id, where the user has already answered at least one other QuestionGroups should
            1. NOT create a new AnswerSet, it should use the existing AnswerSet
            2. It should create a QuestionAnswer object for each question, related to the AnswerSet by a fk relationship
            3. It should redirect to the finish url.
        """
        self.assert_(False, 'Not yet implemented')
        
    def test_handle_next_questiongroup_form_post_success_retry(self):
        """
            In this scenario the user has already completed the first group in the questionnaire, but is retrying/editing their response
            A valid post request will:
            1. NOT create a new AnswerSet
            2. Will create new QuestionAnswer objects only for those questions that have changed, but not for answers which are the same
            (these objects should remain unchanged)
            3. It should redirect to the handle_next_questiongroup_form url specifying the questionnaire id and the 
            id of the next question group for the questionniare (in this case there is one as that is how we setup the fixture)
        """
        
        self.assert_(False, 'Not yet implemented')
        
    def test_handle_next_questiongroup_form_post_failure(self):
        
        """
            An invalid POST request to ''handle_next_questiongroup_form'' view specifying a valid questionnaire id 
            where this is the first request made on a quesstionnaire that the user has not previously attempted should:
            1. Not create an Answerset, or any QuestionAnswer objects
            2. Should redisplay the original form, with appropriate error messages
        
        """
        
        self.assert_(False, 'Not yet implemented')
        
    def test_finish_view(self):
        """
            A GET request to the ''finish'' view should :
            1. return a 200 HTTPResponse
            2. Render the finish.html template
        """
        resp = self.client.get('/questionnaire/finish/')
        self.assertEqual(resp.status_code, 200, 'finish page should be shown')
        self.assertTemplateUsed('finish.html') 
        
        
        
    def test_display_question_answer_invalid_questionnaire(self):
        """
            GET request to ''display_question_answer'' with an invalid question id (ie it doesn't exist)(but logged in) should:
            1. yield a http 404 response
        """
        self.assert_(False, 'Not yet implemented')
        
    def test_display_question_answer_valid_questionnaire_not_logged_in(self):
        """
            GET request to ''display_question_answer'' without being logged in should:
            1. redirect to the default login url
        """
        response = self.client.get('/questionnaire/Answer/1/')
        self.assertEquals (302, response.status_code)
        
        
    def test_display_question_answer_valid_questionnaire_not_answered(self):
        """
            GET request to ''display_question_answer'' with a logged in user and a valid question id but one that has not been answered
            should :
            1. return htt 200 response
            2. template used should be questionAnswer.html
            3. context should not contain any answers (which will cause the template to show that you have no answers)
        """
        self.assert_(False, 'Not yet implemented')
        
    def test_display_question_answer_valid_questionnaire_partialy_answered(self):
        """
            GET request to ''display_question_answer'' with a logged in user and a valid question id for a questionnaire that
            has been partially answered should:
            1. return htt 200 response
            2. template used should be questionAnswer.html
            3. context should contain the answers in such a way that can be rendered by their group
            4. Any unanswered questions should show that they haven't yet been answered
        """
        self.assert_(False, 'Not yet implemented')
        
    def test_display_question_answer_valid_questionnaire_fully_answered(self):
        """
            GET request to ''display_question_answer'' with a logged in user and a valid question id for a questionnaire that
            has been partially answered should:
            1. return htt 200 response
            2. template used should be questionAnswer.html
            3. context should contain the answers in such a way that can be rendered by their group
        """
        self.assert_(False, 'Not yet implemented')
    
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
        self.assert_(False, 'Not yet implemented')
        
        