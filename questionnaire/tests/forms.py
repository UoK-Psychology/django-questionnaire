'''
Created on 26 Jul 2012

@author: jjm20
'''
from django.test import TestCase
from questionnaire.forms import get_choices, generate_charfield, generate_textfield, generate_boolean_field, generate_select_dropdown_field, generate_radioselect_field, generate_multiplechoice_field, FIELD_TYPES, make_question_group_form
from questionnaire.models import Question, Questionnaire, QuestionGroup
from django.forms import Textarea, TextInput, BooleanField, ChoiceField, RadioSelect,CheckboxSelectMultiple, CharField, BaseForm
from django.forms.fields import  MultipleChoiceField
class FormsTestCase(TestCase):
    
    fixtures = ['test_questionnaire_fixtures.json']
    
    
    def test_get_choices_question_with_options(self):
        '''
            Assuming that we pass this function a question object that has options defined
            we should get back:
            1. A list of tuples (option text, option text)
        '''
        
        tuple_choices = [(u'Radio 1',u'Radio 1'), (u' Radio 2',u' Radio 2'), (u' Radio 3',u' Radio 3')]
        choices_question = Question.objects.get(pk=4)
        get_choices_test = get_choices(choices_question)
        self.assertEqual(get_choices_test, tuple_choices)
        
    def test_get_choices_question_without_options(self):
        '''
            If we pass this function a question object that had no options defined we should get back
            None
        '''
        choices_question = Question.objects.create(label='test', field_type='select_dropdown_field', selectoptions=None)
        self.assertRaises(AttributeError, get_choices, choices_question)
        
    def test_get_choices_not_a_question(self):
        '''
            If we pass this function anything other than a question object it should raise a TypeError
        '''
        choices_question = Questionnaire.objects.get(pk=1)
        self.assertRaises(AttributeError, get_choices, choices_question)
        
    def test_generate_charfield(self):
        '''
            This should return us a Charfield with a max length of 100, and a TextInput widget
        '''
        self.assertIsInstance(generate_charfield(), CharField)
        self.assertEqual(generate_charfield().max_length, 100, 'max length return should be 100')
        self.assertIsInstance(generate_charfield().widget, TextInput)
        
    def test_generate_textfield(self):
        '''
            This should return us a Charfield without a max length specified, and using a TextArea widget
        '''
        self.assertEqual(generate_textfield().max_length, None, 'max length should be Not Set')        
        self.assertIsInstance(generate_textfield(), CharField, 'this returns a charfield!')
        self.assertIsInstance(generate_textfield().widget, Textarea)
        
        
        
    def test_generate_boolean_field(self):
        '''
            This should return a BooleanField object defaulting to false
        '''
        self.assertIsInstance(generate_boolean_field(), BooleanField, 'The return class should be boolean field')
        self.assertEqual(generate_boolean_field().initial, False, 'Default value for booleanField is false')
        
        
    def test_generate_select_dropdown_field(self):
        '''
            This should return a Charfield with the choices attribute set to an empty list (to be populated later)
        '''
        self.assertIsInstance(generate_select_dropdown_field(), ChoiceField )
        self.assertEqual(generate_select_dropdown_field().choices, [])

        
    def test_generate_radioselect_field(self):
        '''
            This should return a ChoiceField with a RadioSelect widget and the choices attribute set to an empty list
        '''
        self.assertIsInstance(generate_radioselect_field(), ChoiceField)
        self.assertIsInstance(generate_radioselect_field().widget, RadioSelect )        
        self.assertEqual(generate_radioselect_field().choices, [])
        
    def test_generate_multiplechoice_field(self):
        '''
            This should return a MultipleChoiceField with the choices attribute set to an empty list and a CheckboxSelectMultiple widget
        '''
        self.assertIsInstance(generate_multiplechoice_field(), MultipleChoiceField)
        self.assertIsInstance(generate_multiplechoice_field().widget, CheckboxSelectMultiple)
        self.assertEqual(generate_multiplechoice_field().choices, [])

     
    def test_FIELD_TYPES_dict(self):   
        '''
            charfield should map to ``generate_charfield``
            textfield should map to ``generate_textfield``
            booleanfield should map to ``generate_boolean_field``,
            select_dropdown_fieldshould map to ``generate_select_dropdown_field``,
            radioselectfield should map to ``generate_radioselect_field``,
            multiplechoicefield should map to ``generate_multiplechoice_field``,
        '''

        self.assertEqual(FIELD_TYPES['charfield'], generate_charfield)
        self.assertEqual(FIELD_TYPES['textfield'], generate_textfield)
        self.assertEqual(FIELD_TYPES['booleanfield'], generate_boolean_field)
        self.assertEqual(FIELD_TYPES['select_dropdown_field'], generate_select_dropdown_field)
        self.assertEqual(FIELD_TYPES['radioselectfield'], generate_radioselect_field)
        self.assertEqual(FIELD_TYPES['multiplechoicefield'], generate_multiplechoice_field)
        
        
class FormsTestCase_WithFixture(TestCase):
    
    fixtures = ['test_questionnaire_fixtures.json']
    
    def test_make_question_group_form(self):
        '''
            The fixture should define a questiongroup that has one of each of the question types
            This function should return a BaseForm object and interoggation of its fields should
            be done to ensure that the correct fields have been generated, eg does the first name field have 
            the correct label and is its field properly mapped according to its questiontype?
        '''
        questiongroup_1 = QuestionGroup.objects.get(pk=1)
        questiongroup_2 = QuestionGroup.objects.get(pk=2)
        
        test_make_question_group_form_1 = make_question_group_form(questiongroup_1,1)
        test_make_question_group_form_2 = make_question_group_form(questiongroup_2,1)
        
        dictionary_1 = test_make_question_group_form_1.__name__
        dictionary_2 = test_make_question_group_form_2.__base__
        
        
        print test_make_question_group_form_1
        print dictionary_1
        print dictionary_1['base_fields']
        print dictionary_2
        print dictionary_2['base_fields']
        
        