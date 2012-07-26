from django.test import TestCase


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
        self.assert_(False, 'Not yet implemented')
       
    def test_required_fields(self):
        '''
            label and field_type are mandatory, you should not be able to save without these fields
            you should be able to save without selectoptions
        '''
        self.assert_(False, 'Not yet implemented')
         
    def test_save(self):
        '''
            If the field type is not either select_dropdown_field, radioselectfield ormultiplechoicefield
            then the selectoptions should be set as None prior to saving (even if select options have been set)
        '''
        self.assert_(False, 'Not yet implemented')

        
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
        
        
