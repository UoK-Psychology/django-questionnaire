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

        get_choices_test = get_choices(choices_question)
        self.assertEqual(get_choices_test, None)
        
    def test_get_choices_not_a_question(self):
        '''
            If we pass this function anything other than a question object it should raise an AttributeError
            Raising AttributeError is choosen because eventhough the method error type are using TypeError and
            ValueError, the return value always shows AttributeError
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
        self.assertEqual(generate_boolean_field().initial, True, 'Default value for booleanField is True')
        
        
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
    
    fixtures = ['forms_test_fixture.json']
    
    def assertQuestionType(self, question_type,question):
            
        assertion_map = {'charfield':(CharField, TextInput,None), 
         'textfield': (CharField, Textarea, None), 
         'booleanfield': (BooleanField, None, None),
         'select_dropdown_field':(ChoiceField,None, list),
         'radioselectfield':(ChoiceField,RadioSelect, list),
         'multiplechoicefield':(MultipleChoiceField,CheckboxSelectMultiple,list)}
        
        assertions = assertion_map[question_type]
        
        
        self.assertIsInstance(question , assertions[0])
        
        if assertions[1] != None:
            self.assertIsInstance(question.widget , assertions[1])
        if assertions[2] != None:
            self.assertIsInstance(question.choices , assertions[2])

    def test_make_question_group_form(self):
        '''
            The fixture should define a questiongroup that has one of each of the question types
            This function should return a BaseForm object and interoggation of its fields should
            be done to ensure that the correct fields have been generated, eg does the first name field have 
            the correct label and is its field properly mapped according to its questiontype?
        '''
        

        test_form = make_question_group_form(QuestionGroup.objects.get(pk=1),1)
        
        
        self.assertTrue(issubclass(test_form, BaseForm))

        expected = [    ('question 1','charfield'),
                        ('question 2','textfield'),
                        ('question 3','booleanfield'),
                        ('question 4','select_dropdown_field'),
                        ('question 5','radioselectfield'),
                        ('question 6','multiplechoicefield'),]
       
        for index in range(len(test_form.base_fields)):
                
            self.assertEqual(test_form.base_fields.value_for_index(index).label, expected[index][0])
            self.assertQuestionType(expected[index][1], test_form.base_fields.value_for_index(index)) 

            
        

        
        