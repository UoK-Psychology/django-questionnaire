from django.test import TestCase
from django.db import models
from questionnaire.models import QuestionAnswer, AnswerSet, Question, QuestionGroup, Questionnaire, FIELD_TYPE_CHOICES, QuestionGroup_order, Question_order, CustomListField,\
    LatestQuestionAnswer
from django.db.models.fields import CharField
from django.db import IntegrityError
import mock
from mock import MagicMock
from django.contrib.auth.models import User



class CustomListFieldTests(TestCase):
    fixtures = ['test_questionnaire_fixtures.json']
    def test_init(self):
        '''
            A new Custom List Field should have following attributes:
            1. Default=None
            2. Null=True
            3. blank=True
            4. help_text = non empty string (don't test the exact wording as this may change!)
            5. token=,
            
            and it should be a subclass of TextField
        '''
        string_test = 'A,B,C'
        new_custom_list = CustomListField(string_test)
        empty_string = ''
        
        self.assertEqual(new_custom_list.default, None)
        self.assertEqual(new_custom_list.null, True)
        self.assertEqual(new_custom_list.blank, True)
        self.assertEqual(new_custom_list.token, ',')
        self.assertNotEqual(new_custom_list.help_text, empty_string)
        self.assertTrue(isinstance(new_custom_list, models.TextField), 'CustomListField is an instance of TextField')
        


        
        
    def test_toPython_default(self):
        '''
           Given a string that is comma demlimited this should return you  a list of strings split by the comma
        '''
        string = 'A,B,C'
        expected_list = ['A', 'B', 'C']
        new_custom_list = CustomListField(string).to_python(string)
        self.assertEqual(new_custom_list, expected_list, 'The new custom list will return list as expected')
        self.assertEqual(type(new_custom_list), list, 'The string with delimiter returns object type list')
        
        
        
        
    def test_toPython_customized(self):
        '''
           If a token is specified e.g. | then a string that is delimited with this is returned a s a list split by it
        '''
        string = 'A!B!C'
        expected_list = ['A', 'B', 'C']
        new_custom_list = CustomListField(string, token = '!').to_python(string)
        self.assertEqual(new_custom_list, expected_list)
        
       
        
    def test_toPython_empy_null_string(self):
        '''
           if the value is empty or None, should return an empty list, not an error.
        '''
        string = ''        
        new_custom_list = CustomListField(string).to_python(string)        
        self.assertEqual(new_custom_list, None, 'Empty list will return None, instead of Error')

        
    def test_db_prep_value_default(self):
        '''
            Should return a string delimited by a comma based on the value passed in 
        '''
        string = 'A,B,C'
        expected_list = ['A', 'B', 'C']
        new_custom_list = CustomListField(string)

        get_db_prep_value = new_custom_list.get_db_prep_value(expected_list, expected_list)
        self.assertEqual(get_db_prep_value, string)
        
    
    def test_db_prep_value_custom(self):
        '''
            Should return a string delimited by whatever was specified as the token based on the value passed in 
        '''
        string = 'A!B!C'
        value = ['A', 'B', 'C']
        output = CustomListField(string, token = '!').get_db_prep_value(value)
        self.assertEqual(string, output)
    

        
class QuestionTestCase(TestCase):
    
    
    def test_all_fields(self):
        '''
            A Question object should define:
            1.Label which is a Charfield, max_length = 100
            2.field_type whcih is a charfield with choices:
                a. charfield
                b. textfield
                c. booleanfield
                d. select_dropdown_field
                e. radioselectfield
                f. multiplechoicefield
            3. selectoptions which is a CustomListField
        '''
        
        question_test = Question._meta
        
        self.assertEqual(question_test.get_field('label').max_length, 255, 'length of Charfield should be 255')
        self.assertIsInstance(question_test.get_field('label'), CharField)
        self.assertEqual(question_test.get_field('field_type').choices, FIELD_TYPE_CHOICES)
        self.assertIsInstance(question_test.get_field('selectoptions'), CustomListField)
        
        
    def test_required_fields(self):
        '''
            label and field_type are mandatory, you should not be able to save without these fields
            you should be able to save without selectoptions
        '''
        
        self.assertRaises(IntegrityError, Question.objects.create(label="test_question_without_field_type").save() )
        self.assertRaises(IntegrityError, Question.objects.create(field_type='charfield').save() )
         
    def test_save(self):
        '''
            If the field type is not either select_dropdown_field, radioselectfield or multiplechoicefield
            then the selectoptions should be set as None prior to saving (even if select options have been set)
        '''
        question_test1 = Question.objects.create(label='question_test1', field_type='textfield', selectoptions='Select 1,Select 2,Select 3')
        question_test2 = Question.objects.create(label='question_test2', field_type='charfield', selectoptions='Select 1,Select 2,Select 3')
        question_test3 = Question.objects.create(label='question_test3', field_type='boolean', selectoptions='Select 1,Select 2,Select 3')
        question_test4 = Question.objects.create(label='question_test4', field_type='select_dropdown_field', selectoptions='Select 1,Select 2,Select 3')
        question_test5 = Question.objects.create(label='question_test5', field_type='radioselectfield', selectoptions='Select 1,Select 2,Select 3')
        question_test6 = Question.objects.create(label='question_test6', field_type='multiplechoicefield', selectoptions='Select 1,Select 2,Select 3')
        question_test1.save()
        question_test2.save()
        question_test3.save()
        question_test4.save()
        question_test5.save()
        question_test6.save()
        self.assertEqual(question_test1.selectoptions, None, 'question_test1.selectoption is not None')
        self.assertEqual(question_test2.selectoptions, None, 'question_test2.selectoption is not None')
        self.assertEqual(question_test3.selectoptions, None, 'question_test3.selectoption is not None')
        self.assertNotEqual(question_test4.selectoptions, None, 'question_test4.selectoption is None')
        self.assertNotEqual(question_test5.selectoptions, None, 'question_test5.selectoption is None')
        self.assertNotEqual(question_test6.selectoptions, None, 'question_test6.selectoption is None')
        
        
class QuestionGroupTestCase(TestCase):
    fixtures = ['test_questionnaire_fixtures_formodels.json']
    
    def test_fields_all_fields(self):
        '''
            A QuestionGroup must have :
            1. name - which is a charfield, has a max length of 255 and should be unique and *required*
            2. questions ManyToMay field related to Question through question_order
        '''
        questiongroup_test = QuestionGroup._meta
        

        self.assertEqual(questiongroup_test.get_field('name').max_length , 255)
        self.assertIsInstance(questiongroup_test.get_field('name'), CharField)
        
        QuestionGroup_object = QuestionGroup.objects.get(pk=1)
        QuestionGroup_Through = QuestionGroup_object.questions.through.__name__
        self.assertEqual(QuestionGroup_Through, 'Question_order')

        
        
        
    def test_required_fields(self):
        '''
            Name is required so you should not be able to save the object without it
        '''
          
        self.assertRaises(IntegrityError, QuestionGroup.objects.create(name='').save() )
          
    def test_get_ordered_questions(self):
        '''
            This function should give you a list of Question objects, this list should be based upon the order_info
            provided by the through relationship with Question_order
        '''
        question_group_test = QuestionGroup.objects.get(pk=1)
        questions = question_group_test.get_ordered_questions()
        question_order1 = Question_order.objects.get(pk=1)
        question_order2 = Question_order.objects.get(pk=2)
        question_order3 = Question_order.objects.get(pk=3) 
        self.assertEqual(questions[0].label, question_order1.question.label)
        self.assertEqual(questions[1].label, question_order2.question.label)
        self.assertEqual(questions[2].label, question_order3.question.label)
        
    def test_set_context(self):
        '''
            If you pass in questionnaire and user objects, this function will set  and
            _user_context respectively with these values. If you pass in anything else 
            then an AttributeError will be thrown
        '''
        test_user = User.objects.create_user('test', 'test@test.com', 'password')
        test_group = QuestionGroup.objects.get(pk=1)
        test_questionnaire = Questionnaire.objects.get(id=1)
        self.assertIsNone(test_group._questionnaire_context)#should start out empty
        self.assertIsNone(test_group._user_context)#should start out empty
        
        self.assertRaises(AttributeError, test_group.set_context, 'not a questionnaire', test_user)
        self.assertRaises(AttributeError, test_group.set_context, test_questionnaire, 'not a user')
        
        test_group.set_context(test_questionnaire, test_user)
        self.assertEqual(test_group._questionnaire_context, test_questionnaire)
        self.assertEqual(test_group._user_context, test_user)
        
    def test_clear_questionnaire_context(self):
        '''
            This will set _questionnaire_context to None
        '''
        test_user = User.objects.create_user('test', 'test@test.com', 'password')
        test_group = QuestionGroup.objects.get(pk=1)
        test_questionnaire = Questionnaire.objects.get(id=1)
        
        self.assertIsNone(test_group._questionnaire_context)#should start out empty
        self.assertIsNone(test_group._user_context)#should start out empty
        
        test_group.clear_context()
        self.assertIsNone(test_group._questionnaire_context)
        self.assertIsNone(test_group._user_context)
        
        test_group._questionnaire_context = test_questionnaire
        test_group._user_context = test_user
        test_group.clear_context()
        self.assertIsNone(test_group._questionnaire_context)
        self.assertIsNone(test_group._user_context)

        
    def test_is_complete_with_argument(self):
        '''
            If you pass in a questionnaire as the questionnaire_context argument, this function should
            will get the answer set that links itself with this questionnaire. If this
            answerset is complete then it will return True otherwise it will return False
        '''

        self.assertTrue(False)
        
    def test_is_complete_with_invalide_argument(self):
        '''
            If you pass in anyhting other than a questionnaire as questionnaire_context
            argument you will get a AttributrError.
        '''
        
        self.assertTrue(False)
        
    def test_is_complete_without_argument_context_set(self):
        '''
            If you don't pass in a questionnaire_context then the function will fall
            back to using the _questionnaire_context field, if this is not None then
            it will perform the same function as if you had passed this into the
            function (the tests should be identical)
        '''
        
        self.assertTrue(False)
        
    def test_is_complete_without_argument_context_not_set(self):
        '''
            If you don't pass in a questionnaire_context argument , and no
            _questionnaire_context is set, then this will return False.
        
        '''
        
        self.assertTrue(False)
       
class QuestionnaireTestCase(TestCase):
    fixtures = ['test_questionnaire_fixtures_formodels.json']
    
    def test_fields_all_fields(self):
        '''
            A Questionaire must have :
            1. name - which is a charfield, has a max length of 250 and should be unique and *required*
            2. questiongroups ManyToMay field related to QuestionGroup through questionGroup_order
        '''
        
        questionnaire_test = Questionnaire._meta
        self.assertEqual(questionnaire_test.get_field('name').max_length, 250)
        self.assertIsInstance(questionnaire_test.get_field('name'), CharField)        
        Questionnaire_object = Questionnaire.objects.get(pk=1)
        Questionnaire_Through = Questionnaire_object.questiongroup.through.__name__
        self.assertEqual(Questionnaire_Through, 'QuestionGroup_order')
        
         
    def test_required_fields(self):
        '''
            Name is required so you should not be able to save the object without it
        '''
        self.assertRaises(IntegrityError, Questionnaire.objects.create(name='').save() )
        
    def test_get_ordered_question_group(self):
        '''
            This function should give you a list of QuestionGroup objects, this list should be based upon the order_info
            provided by the through relationship with QuestionGroup_order
        '''
        questionnaire_test = Questionnaire.objects.get(pk=1)
        question_group = questionnaire_test.get_ordered_groups()
        question_group1 = QuestionGroup_order.objects.get(pk=1)
        question_group2 = QuestionGroup_order.objects.get(pk=2) 
        self.assertEqual(question_group[0].questiongroup.name, question_group1.questiongroup.name)
        self.assertEqual(question_group[1].questiongroup.name, question_group2.questiongroup.name)
        
    def test_get_group_for_index_invalid_index(self):
        '''
            Thorws an index error if there isn't a group at this index
        '''
        
        questionnaire_test = Questionnaire.objects.get(pk=1)
        
        self.assertRaises(IndexError, questionnaire_test.get_group_for_index, 5)
        
    def test_get_group_for_index_valid_index(self):
        '''
            If this index exists then we should get the correct group, and an integer representing
            the number of groups that are left in the sequence.
        '''
        questionnaire_test = Questionnaire.objects.get(pk=1)
        question_group = QuestionGroup.objects.get(pk=1)
        
        group, count = questionnaire_test.get_group_for_index(0)
        
        self.assertEqual(question_group, group)
        self.assertEqual(1, count)#there were two groups so after this index there should be 2 remaining
        
    def test_get_group_for_index_last_index(self):
        '''
            If this is the last index in the sequence of groups zero should be returned
        '''
        questionnaire_test = Questionnaire.objects.get(pk=1)
        question_group = QuestionGroup.objects.get(pk=2)
        
        group, count = questionnaire_test.get_group_for_index(1)
        
        self.assertEqual(question_group, group)
        self.assertEqual(0, count)#there were two groups so after this index there should be 2 remaining    
    
    def test_add_question_group(self):
        '''
            first group, should be added with order_info of 1
            non first group, should be added with the next order_info in the sequence, eg. if the most recent order_info is 3 then
            this group should be added with order_info = 4
            questiongroup, not a questiongroup - raise attributeerror
        '''
        
        test_questionnaire = Questionnaire.objects.create(name='test_questionnaire')
        test_group = QuestionGroup.objects.create(name='test_question_group')
        another_test_group = QuestionGroup.objects.create(name='test_question_group2')
        
        groups_in_order = QuestionGroup_order.objects.filter(questionnaire=test_questionnaire).order_by('order_info')
        
        self.assertEqual(0, len(groups_in_order))
        
        test_questionnaire.add_question_group(test_group)
        
        groups_in_order = QuestionGroup_order.objects.filter(questionnaire=test_questionnaire).order_by('order_info')
        
        self.assertEqual(1, len(groups_in_order))
        self.assertEqual(QuestionGroup_order.objects.get(questiongroup=test_group, questionnaire=test_questionnaire).order_info, 1)
        
        #add another group
        test_questionnaire.add_question_group(another_test_group)
        groups_in_order = QuestionGroup_order.objects.filter(questionnaire=test_questionnaire).order_by('order_info')
        
        self.assertEqual(2, len(groups_in_order))
        self.assertEqual(QuestionGroup_order.objects.get(questiongroup=another_test_group, questionnaire=test_questionnaire).order_info, 2)
        
        #try adding an invalid group
        self.assertRaises(AttributeError, test_questionnaire.add_question_group, 'not a QuestionGroup')

        
class Questiongroup_OrderTestCase(TestCase):
    fixtures = ['test_questionnaire_fixtures_formodels.json']
    
    def test_fields(self):
        '''
            QuestionGroup_order should have the following fields (all of which are required):
            questiongroup = ForeignKey relationship with QuestionGroup
            questionnaire = ForeignKey relationship with Questionnaire
            order_info = IntegerField
        '''
        object_test = QuestionGroup_order.objects.get(pk=1)
        self.assertIsInstance(object_test.questiongroup, QuestionGroup)
        self.assertIsInstance(object_test.questionnaire, Questionnaire)
        self.assertIsInstance(object_test.order_info, int)
        
    def test_required_fields(self):
        '''
            You shouldn't be able to make a QuestionGroup_order without any of the fields
        '''
        self.assertRaises(IntegrityError, QuestionGroup_order.objects.create)
        

class Question_OrderTestCase(TestCase):
    fixtures = ['test_questionnaire_fixtures_formodels.json']
    
    def test_fields(self):
        '''
            Question_order should have the following fields (all of which are required):
            question = ForeignKey relationship with Question
            questiongroup = ForeignKey relationship with QuestionGroup
            order_info = IntegerField
        '''
        object_test = Question_order.objects.get(pk=1)
        self.assertIsInstance(object_test.question, Question)
        self.assertIsInstance(object_test.questiongroup, QuestionGroup)
        self.assertIsInstance(object_test.order_info, int)
        
    def test_required_fields(self):
        '''
            You shouldn't be able to make a Question_order without any of the fields
        '''
        self.assertRaises(IntegrityError, Question_order.objects.create)
        
    
        
class AnswerSetTestCase(TestCase):  
    fixtures = ['test_questionnaire_fixtures_formodels.json']
    
    def test_fields(self):
        '''
            An AnswerSet should have the following required fields:
            1. User - FK to django.contrib.auth.models.User
            2. questionniare - FK to Questionnaire
        '''
        answer_set_test = AnswerSet._meta
        self.assertEqual(str(answer_set_test.get_field('user')), '<django.db.models.fields.related.ForeignKey: user>',)
        self.assertEqual(str(answer_set_test.get_field('questionnaire')), '<django.db.models.fields.related.ForeignKey: questionnaire>',)
        
    def test_required_fields(self):
        '''
            An AnswerSet should not be able to be saved without all of its fields present
        '''

        
        self.assertRaises(IntegrityError, AnswerSet.objects.create)
        
    def test_get_latest_question_answers(self):
        '''
            This should return a list of only the latest QuestionAnswers that relate to this answerset
            this should be achieved by querying the LatestQuestionAnswer
        ''' 
        #generate an AnswerSet
        
        test_answer_set = AnswerSet(user=User.objects.create_user('test', 'test@test.com', 'test'), 
                                    questionnaire=Questionnaire.objects.get(pk=1),
                                    questiongroup=QuestionGroup.objects.get(pk=1))
        #patch the LatestQuestionAnswer objects function
        with mock.patch('questionnaire.models.LatestQuestionAnswer.objects') as objects_patch:
            
            objects_patch.filter.return_value = [MagicMock(question_answer='questionAnswer1'),MagicMock(question_answer='questionAnswer2')]
            answers = test_answer_set.get_latest_question_answers()#pass the mock in as the self argument
        
            objects_patch.filter.assert_called_once_with(answer_set=test_answer_set)
            self.assertEqual(answers, ['questionAnswer1','questionAnswer2'])
    
class QuestionAnswerTestCase(TestCase):
    fixtures = ['test_questionnaire_fixtures_formodels.json']
    def test_fields(self):
        '''
            A Question Answer should have the following fields:
            1. question - FK to a Question
            2. answer - Charfield max length = 255 can be blank
            3. answer_Set - FK to a AnswerSet object
        '''
        question_answer_test = QuestionAnswer._meta
        self.assertEqual(str(question_answer_test.get_field('question')),'<django.db.models.fields.related.ForeignKey: question>')
        self.assertEqual(str(question_answer_test.get_field('answer')),'<django.db.models.fields.CharField: answer>')
        self.assertEqual(str(question_answer_test.get_field('answer_set')),'<django.db.models.fields.related.ForeignKey: answer_set>')                        
        self.assertEqual(question_answer_test.get_field('answer').max_length,255)
    
    
    def test_required_fields(self):
        '''
            You shouldn't be able to save a QuestionAnswer without question or answer_Set
            However you should be able to do without specifying an answer, and this should be saved as an empty string.
        '''
        self.assertRaises(IntegrityError, QuestionAnswer.objects.create)
        
        
    def test_save_override(self):
        '''
            The overriden save method should ensure that the correct question answert is stored in the 
            LatestQuestionAnswer table
            
            If there is no record for this question in this answer_set then create one with this question answer
            If there is a record, but the latest is not this then update it to make this the latest
            If there is a record, and it is already set to this do nothing
        '''
        #intially we need an answerset
        test_answer_set = AnswerSet(user=User.objects.create_user('test', 'test@test.com', 'test') ,
                                     questionnaire=Questionnaire.objects.get(pk=1), questiongroup=QuestionGroup.objects.get(pk=1))
        
        test_answer_set.save()
        #initialy there shouldnt be any record in the latestquestionanswer so the function should create one
        an_answer = QuestionAnswer(question=Question.objects.get(pk=1),
                                   answer='my answer',
                                   answer_set = test_answer_set)
        an_answer.save()
        self.assertEqual(len(LatestQuestionAnswer.objects.all()), 1)
        self.assertEqual(LatestQuestionAnswer.objects.latest('id').question_answer, an_answer)
        #now if we save a new question answer then the record should be updated
        
        a_new_answer = QuestionAnswer(question=Question.objects.get(pk=1),
                                   answer='my new answer',
                                   answer_set = test_answer_set)
        a_new_answer.save()
        self.assertEqual(len(LatestQuestionAnswer.objects.all()), 1)
        self.assertEqual(LatestQuestionAnswer.objects.latest('id').question_answer, a_new_answer)
        a_new_answer_created = LatestQuestionAnswer.objects.latest('id').created
        
        #then if we save this question asnwer again then nothing should happen
        
        a_new_answer.save()
        self.assertEqual(len(LatestQuestionAnswer.objects.all()), 1)
        self.assertEqual(LatestQuestionAnswer.objects.latest('id').question_answer, a_new_answer)
        self.assertEqual(LatestQuestionAnswer.objects.latest('id').created, a_new_answer_created)#the timestamp should'nt have changed
        
        
        