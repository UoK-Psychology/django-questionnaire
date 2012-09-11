from django.test import TestCase
from questionnaire.forms import get_choices, generate_charfield, generate_textfield, generate_boolean_field, generate_select_dropdown_field, generate_radioselect_field, generate_multiplechoice_field, FIELD_TYPES,\
    QuestionGroupForm, _get_fields_for_group, _convert_answerset_to_intial_data
from questionnaire.models import Question, Questionnaire, QuestionGroup, AnswerSet, QuestionAnswer
from django.forms import Textarea, TextInput, BooleanField, ChoiceField, RadioSelect,CheckboxSelectMultiple, CharField
from django.forms.fields import  MultipleChoiceField, TypedChoiceField
from mock import MagicMock, patch, call
from django.contrib.auth.models import User


class FormsTestCase(TestCase):
    
    fixtures = ['test_questionnaire_fixtures.json']
    
    
    def test_get_choices_question_with_options(self):
        '''
            Assuming that we pass this function a question object that has options defined
            we should get back:
            1. A list of tuples (option text, option text)
        '''
        
        tuple_choices = [(u'Radio 1',u'Radio 1'), (u' Radio 2',u' Radio 2'), (u' Radio 3',u' Radio 3')]
        choices_question = Question.objects.get(pk=5)
        get_choices_test = get_choices(choices_question)
        self.assertEqual(get_choices_test, tuple_choices)
        
    def test_get_choices_question_without_options(self):
        '''
            If we pass this function a question object that had no options defined we should get None back
        '''
        choices_question = Question.objects.create(label='test', field_type='select_dropdown_field', selectoptions=None)
        self.assertEquals(None, get_choices(choices_question)   )    
        
        
        
        
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
            This should return a TypedChoiceField object with yes and no as options
        '''
        self.assertIsInstance(generate_boolean_field(), TypedChoiceField, 'The return class should be boolean field')
        self.assertEqual(generate_boolean_field().choices, [(1,'Yes'),( 0,'No')])
        
        
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
        
    def test_get_fields_for_group(self):
        '''
            Calling this function should create a list of tuples that has the same order as
            the ordered questions in the group, and used the FIELD_TYPES dict to create the 
            fields. As we have already tested the FIELD_TYPE and allof the generator functions
            this test will simply test make sure that the function returns a sortedDict
            in the correct order
        '''
        
        with patch('questionnaire.forms.FIELD_TYPES') as field_dict_mock:
            return_values = [MagicMock(name='mock1'),MagicMock(name='mock2')]
            def side_effect(*attrs):
                return return_values.pop()
                
            
            
            field_function_mock = MagicMock(name='field_function_mock')
            field_function_mock.side_effect = side_effect
            field_dict_mock.__getitem__.return_value = field_function_mock
            
            questiongroup = MagicMock(name='questiongroup')
            
            #prepare a list of mock objects to act as questions when returned by the ordered_question
            questiongroup.get_ordered_questions.return_value = [MagicMock(label='question1', id=1, field_type='type1'),
                                                                        MagicMock(label='question2', id=2, field_type='type2' ),  ]
            with patch('questionnaire.forms.get_choices') as get_choices_mock:
                test_form = _get_fields_for_group(questiongroup=questiongroup)
            
            
           
            self.assertEqual(field_dict_mock.__getitem__.mock_calls , [call('type1'), call('type2')])
            self.assertEqual(test_form[0][0], '1')
            self.assertEqual(test_form[0][1].label, 'question1')
            self.assertEqual(test_form[1][0], '2')
            self.assertEqual(test_form[1][1].label, 'question2')
            self.assertEqual(get_choices_mock.call_count, 2)
            
    def test_convert_answerset_to_intial_data_with_data(self):
        '''
            if we pass in a valid questionanswer object then we should get back
            a dicitonary, that has a entry for eacxh questionsanswer, the key of which is
            the question id and the value of which is the question answer
        '''
        
        test_answer_set = AnswerSet(user=User.objects.create_user('testUser', 'me@home.com', 'testPass'),
                                     questionnaire=Questionnaire.objects.get(pk=1),
                                     questiongroup=QuestionGroup.objects.get(pk=1))
        
        test_answer_set.save()
        #create some answers
        answer1 = QuestionAnswer(question=Question.objects.get(pk=1), answer='answer1', answer_set=test_answer_set)
        answer2 = QuestionAnswer(question=Question.objects.get(pk=2), answer='answer2', answer_set=test_answer_set)
        answer3 = QuestionAnswer(question=Question.objects.get(pk=3), answer='answer3', answer_set=test_answer_set)
        
        answer1.save()
        answer2.save()
        answer3.save()
        
        initial_data = _convert_answerset_to_intial_data(test_answer_set)
        
        self.assertEqual(initial_data[str(answer1.question.id)], answer1.answer)
        self.assertEqual(initial_data[str(answer2.question.id)], answer2.answer)
        self.assertEqual(initial_data[str(answer3.question.id)], answer3.answer)
        self.assertEqual(len(initial_data), 3)
        
    def test_convert_answerset_to_intial_data_with_empty_data(self):
        '''
            if we pass in a valid questionanswer object that has not answers then we should get back
            an empty dicitonary
        '''
        
        test_answer_set = AnswerSet(user=User.objects.create_user('testUser', 'me@home.com', 'testPass'),
                                     questionnaire=Questionnaire.objects.get(pk=1),
                                     questiongroup=QuestionGroup.objects.get(pk=1))
        
        test_answer_set.save()
        
        
        initial_data = _convert_answerset_to_intial_data(test_answer_set)

        self.assertEqual(len(initial_data), 0)
        
    def test_convert_answerset_to_intial_data_with_invalid_argument(self):
        '''
            if we pass in anything other that a valid questionanswer object then we will get a Attribute error thrown
        '''
        self.assertRaises(AttributeError, _convert_answerset_to_intial_data, '123')
        
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

    
class QuestionGroupFormTestCase(TestCase):
    
    
    def test_create_form_no_initial_data(self):
        '''
            If I pass in a valid questiongroup object and valid questionaire_id then I should get back:
            
            an subclass of Form
            it should have fields representative of the questions in the questiongroup
        '''
        #mock the _get_fields_for_group function to return a predefined list of tuples
        with patch('questionnaire.forms._get_fields_for_group') as get_fields_mock:
            mock1 = MagicMock(name='1')
            mock2 = MagicMock(name='1')
            get_fields_mock.return_value = [('1', mock1), ('2', mock2 )]
            question_group = MagicMock('question_group')
            
            test_form = QuestionGroupForm(questiongroup=question_group,  initial=None, data=None)
        
            self.assertEqual(test_form.fields['1'], mock1)#assert that the fields contain the fields expected based on the mocked return value
            self.assertEqual(test_form.fields['2'], mock2)
    def test_create_form_with_initial_data(self):
        '''
            If I do all of the above, but also pass a dictionary as the instance argument then my form
            should have initial data for all of the fields that the question group and the answerset have in common
        '''
        with patch('questionnaire.forms._get_fields_for_group') as get_fields_mock:
            mock1 = MagicMock(name='1')
            mock2 = MagicMock(name='1')
            get_fields_mock.return_value = [('1', mock1), ('2', mock2 )]
            question_group = MagicMock('question_group')
            
            initial_data = {'1':'initial1', '2':'initial2', }
            test_data = {'1':'data1', '2':'data2',}
            test_form = QuestionGroupForm(questiongroup=question_group,initial=initial_data, data=test_data)
        
            #sanity check should be the same as above
            self.assertEqual(test_form.fields['1'], mock1)#assert that the fields contain the fields expected based on the mocked return value
            self.assertEqual(test_form.fields['2'], mock2)
            
            #assert the intial data
            self.assertEqual(test_form.initial['1'], 'initial1')
            self.assertEqual(test_form.initial['2'], 'initial2')
            
            self.assertEqual(test_form.data['1'], 'data1')
            self.assertEqual(test_form.data['2'], 'data2')
    
    @patch('questionnaire.forms._convert_answerset_to_intial_data')        
    def test_create_form_with_initial_answer_set(self, conversion_fucntion_mock):
        '''
            If I do all of the above, but also pass an answer set as the instance argument then my form will call the 
            _convert_answerset_to_intial_data with the answer set function, and use the returned dict as the initial data function
        '''
        conversion_fucntion_mock.return_value = {'1':'initial_answer_1', '2':'initial_answer_2' }
        
        with patch('questionnaire.forms._get_fields_for_group') as get_fields_mock:
            mock1 = MagicMock(name='1')
            mock2 = MagicMock(name='1')
            get_fields_mock.return_value = [('1', mock1), ('2', mock2 )]
            question_group = MagicMock('question_group')
            
            initial_data = AnswerSet()
            test_data = {'1':'data1', '2':'data2',}
            test_form = QuestionGroupForm(questiongroup=question_group,initial=initial_data, data=test_data)
        
            #sanity check should be the same as above
            self.assertEqual(test_form.fields['1'], mock1)#assert that the fields contain the fields expected based on the mocked return value
            self.assertEqual(test_form.fields['2'], mock2)
            
            #assert the intial data
            self.assertEqual(test_form.initial['1'], 'initial_answer_1')
            self.assertEqual(test_form.initial['2'], 'initial_answer_2')
            
            self.assertEqual(test_form.data['1'], 'data1')
            self.assertEqual(test_form.data['2'], 'data2')
            
            conversion_fucntion_mock.assert_called_once_with(initial_data)
        