from django.test import TestCase
from django.db import models
from questionnaire.models import Question, QuestionGroup, Questionnaire, CustomListField


class CustomListFieldTests(TestCase):
    
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
        self.assert_(False, 'Not yet implemented')
        
    def test_toPython_default(self):
        '''
           Given a string that is comma demlimited this should return you  a list of strings split by the comma
        '''
        self.assert_(False, 'Not yet implemented')
        
    def test_toPython_customized(self):
        '''
           If a token is specified e.g. | then a string that is delimited with this is returned a s a list split by it
        '''
        self.assert_(False, 'Not yet implemented')
        
    def test_toPython_empy_null_string(self):
        '''
           if the value is empty or None, should return an empty list, not an error.
        '''
        self.assert_(False, 'Not yet implemented')
        
    def test_db_prep_value_default(self):
        '''
            Should return a string delimited by a comma based on the value passed in 
        '''
        self.assert_(False, 'Not yet implemented')
    
    def test_db_prep_value_custom(self):
        '''
            Should return a string delimited by whatever was specified as the token based on the value passed in 
        '''
        self.assert_(False, 'Not yet implemented')
    
    def test_value_to_string(self):
        '''
            assuming the object passed in is a CustomListField poulated with a value
            this should do the same as test_db_prep_value_default
        '''
        self.assert_(False, 'Not yet implemented')
        
class QuestionTestCase(TestCase):
    fixtures = ['test_questionnaire_fixtures.json']
    
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
        question_label101 = Question.objects.create(label='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 
                                                   field_type='charfield', selectoptions=None)
        self.assertIsInstance(question_label101.label, models.CharField, 'question_label101.label is not an instance of models.CharField')
        self.assertLessEqual(len(question_label101.label), 100,'label length is greater than 100')
        self.assertEqual(question_label101.field_type, 'charfield', 'field_type is not charfield')
        self.assertIsInstance(question_label101.field_type, CustomListField, 'field_type is not an instance of CustomListField')
        
        question_textfield = Question.objects.create(label='question_textfield', field_type='charfield', selectoptions=None)
        self.assertEqual(question_textfield.field_type, 'textfield', 'field_type is not textfield')
        
        question_booleanfield = Question.objects.create(label='question_booleanfield', field_type='charfield', selectoptions=None)
        self.assertEqual(question_booleanfield.field_type, 'boolean', 'field_type is not booleanfield')
        
        question_select_dropdown_field = Question.objects.create(label='question_select_dropdown_field', field_type='select_dropdown_field', selectoptions=None)
        self.assertEqual(question_select_dropdown_field.field_type, 'select_dropdown_field', 'field_type is not select_dropdown_field')
        
        question_radioselectfield = Question.objects.create(label='question_radioselectfield', field_type='radioselectfield', selectoptions=None)
        self.assertEqual(question_radioselectfield.field_type, 'radioselectfield', 'field_type is not radioselectfield')
        
        question_multiplechoicefield = Question.objects.create(label='question_multiplechoicefield', field_type='multiplechoicefield', selectoptions=None)
        self.assertEqual(question_multiplechoicefield.field_type, 'multiplechoicefield', 'field_type is not multiplechoicefield')
        
    def test_required_fields(self):
        '''
            label and field_type are mandatory, you should not be able to save without these fields
            you should be able to save without selectoptions
        '''
        question_test = Question.objects.create(label='question_test', field_type=None, selectoptions=None)
        question_test1 = Question.objects.create(label='question_test1', field_type='charfield', selectoptions=None)
        
        self.assertFalse(question_test.save(),"can't be saved without field_type")
        self.assertTrue(question_test1.save(), 'can be saved')
         
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
        '''
        self.assertTrue(question_test1.save(), 'question_test1 is not saved')
        self.assertTrue(question_test2.save(), 'question_test2 is not saved')
        self.assertTrue(question_test3.save(), 'question_test3 is not saved')
        self.assertTrue(question_test4.save(), 'question_test4 is not saved')
        self.assertTrue(question_test5.save(), 'question_test5 is not saved')
        self.assertTrue(question_test6.save(), 'question_test6 is not saved')
        '''
        question_test1.save()
        question_test2.save()
        question_test3.save()
        question_test4.save()
        question_test5.save()
        question_test6.save()
        self.assertEqual(question_test1.selectoption, None, 'question_test1.selectoption is not None')
        self.assertEqual(question_test2.selectoption, None, 'question_test2.selectoption is not None')
        self.assertEqual(question_test3.selectoption, None, 'question_test3.selectoption is not None')
        self.assertNotEqual(question_test4.selectoption, None, 'question_test4.selectoption is None')
        self.assertNotEqual(question_test5.selectoption, None, 'question_test5.selectoption is None')
        self.assertNotEqual(question_test6.selectoption, None, 'question_test6.selectoption is None')
        
        
class QuestionGroupTestCase(TestCase):
    
    def test_fields_all_fields(self):
        '''
            A QuestionGroup must have :
            1. name - which is a charfield, has a max length of 255 and should be unique and *required*
            2. questions ManyToMay field related to Question through question_order
        '''
        self.assert_(False, 'Not yet implemented')
        
    def test_required_fields(self):
        '''
            Name is required so you should not be able to save the object without it
        '''
        self.assert_(False, 'Not yet implemented')
        
    def test_get_ordered_questions(self):
        '''
            This function should give you a list of Question objects, this list should be based upon the order_info
            provided by the through relationship with Question_order
        '''
        self.assert_(False, 'Not yet implemented')
        
    
        
class QuestionnaireTestCase(TestCase):
    def test_fields_all_fields(self):
        '''
            A Questionaire must have :
            1. name - which is a charfield, has a max length of 255 and should be unique and *required*
            2. questiongroups ManyToMay field related to QuestionGroup through questionGroup_order
        '''
        self.assert_(False, 'Not yet implemented')
        
    def test_required_fields(self):
        '''
            Name is required so you should not be able to save the object without it
        '''
        self.assert_(False, 'Not yet implemented')
        
    def test_get_ordered_questions(self):
        '''
            This function should give you a list of QuestionGroub objects, this list should be based upon the order_info
            provided by the through relationship with QuestionGroup_order
        '''
        self.assert_(False, 'Not yet implemented')
        
class Questiongroup_OrderTestCase(TestCase):
    
    def test_fields(self):
        '''
            QuestionGroup_order should have the following fields (all of which are required):
            questiongroup = ForeignKey relationship with QuestionGroup
            questionnaire = ForeignKey relationship with Questionnaire
            order_info = IntegerField
        '''
        self.assert_(False, 'Not yet implemented')
        
    def test_required_fields(self):
        '''
            You shouldn't be able to make a QuestionGroup_order without any of the fields
        '''
        self.assert_(False, 'Not yet implemented')
        
    
        
class Question_OrderTestCase(TestCase):
    
    def test_fields(self):
        '''
            Question_order should have the following fields (all of which are required):
            question = ForeignKey relationship with Question
            questionnaire = ForeignKey relationship with Questionnaire
            order_info = IntegerField
        '''
        self.assert_(False, 'Not yet implemented')
        
    def test_required_fields(self):
        '''
            You shouldn't be able to make a QuestionGroup_order without any of the fields
        '''
        self.assert_(False, 'Not yet implemented')
        
    
        
class AnswerSetTestCase(TestCase):
    
    def test_fields(self):
        '''
            An AnswerSet should have the following required fields:
            1. User - FK to django.auth.models.User
            2. questionniare - FK to Questionnaire
        '''
        self.assert_(False, 'Not yet implemented')
        
    def test_required_fields(self):
        '''
            An AnswerSet should not be able to be saved without all of its fields present
        '''
        self.assert_(False, 'Not yet implemented')
        
    
class QuestionAnswerTestCase(TestCase):
    
    def test_fields(self):
        '''
            A Question Answer should ahve the following fields:
            1. question - FK to a Question
            2. answer - Charfield max length = 255 can be blank
            3. answer_Set - FK to a AnswerSet object
        '''
        self.assert_(False, 'Not yet implemented')
        
    def test_required_fields(self):
        '''
            You shouldn't be able to save a QuestionAnswer without question or answer_Set
            However you should be able to do without specifying an answer, and this should be saved as an empty string.
        '''
        
        
