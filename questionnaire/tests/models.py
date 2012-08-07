from django.test import TestCase
from django.db import models
from questionnaire.models import QuestionAnswer, AnswerSet, Question, QuestionGroup, Questionnaire, FIELD_TYPE_CHOICES, QuestionGroup_order, Question_order, CustomListField
from django.db.models.fields import CharField



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
        string = 'A,B,C'
        
        new_custom_list = CustomListField(string).token(token = '.' )
        print new_custom_list
        
        self.assert_(False, 'Not yet implemented')
        
    def test_toPython_empy_null_string(self):
        '''
           if the value is empty or None, should return an empty list, not an error.
        '''
        string = ''
        #expected_list = []
        new_custom_list = CustomListField(string).to_python(string)
        #self.assertEqual(new_custom_list, expected_list, 'The new custom list will return empty list as expected')
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
        self.assert_(False, 'Not yet implemented')
    
    def test_value_to_string(self):
        '''
            assuming the object passed in is a CustomListField poulated with a value
            this should do the same as test_db_prep_value_default
        '''
        string = 'A,B,C'
        expected_list = ['A', 'B', 'C']
        new_custom_list = CustomListField(string)
        value_to_string = new_custom_list.value_to_string(new_custom_list)
        print value_to_string
        
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
        #self.assertEqual(questiongroup_test.get_field('name').max_length , 255)
        self.assertIsInstance(questiongroup_test.get_field('name'), CharField)
        
        QuestionGroup_object = QuestionGroup.objects.get(pk=1)
        QuestionGroup_Through = QuestionGroup_object.questions.through.__name__
        self.assertEqual(QuestionGroup_Through, 'Question_order')

        
        
        
    def test_required_fields(self):
        '''
            Name is required so you should not be able to save the object without it
        '''
        question_group_test1 = QuestionGroup.objects.create()
        self.assertFalse(question_group_test1.save())
          
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
       
class QuestionnaireTestCase(TestCase):
    fixtures = ['test_questionnaire_fixtures_formodels.json']
    
    def test_fields_all_fields(self):
        '''
            A Questionaire must have :
            1. name - which is a charfield, has a max length of 255 and should be unique and *required*
            2. questiongroups ManyToMay field related to QuestionGroup through questionGroup_order
        '''
        
        questionnaire_test = Questionnaire._meta
        #self.assertEqual(questionnaire_test.get_field('name').max_length, 255)
        self.assertIsInstance(questionnaire_test.get_field('name'), CharField)        
        Questionnaire_object = Questionnaire.objects.get(pk=1)
        Questionnaire_Through = Questionnaire_object.questiongroup.through.__name__
        self.assertEqual(Questionnaire_Through, 'QuestionGroup_order')
        
         
    def test_required_fields(self):
        '''
            Name is required so you should not be able to save the object without it
        '''
        questionnaire_test1 = Questionnaire.objects.create()
        self.assertFalse(questionnaire_test1.save())
        
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
        self.assertFalse(QuestionGroup_order.objects.create(), 'can not be created')
        

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
        self.assertFalse(Question_order.objects.create(), 'can not be created')
        
    
        
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
        object_test = AnswerSet.objects.create()
        self.assertRaisesMessage('IntegrityError', 'answer_set.user_id may not be NULL', object_test.save())
        
    
class QuestionAnswerTestCase(TestCase):
    
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