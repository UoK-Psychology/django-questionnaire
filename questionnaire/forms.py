from django import forms
from django.forms.fields import CharField,BooleanField,ChoiceField,MultipleChoiceField,\
    TypedChoiceField
from django.forms.widgets import RadioSelect, CheckboxInput
from questionnaire.models import AnswerSet

  


def get_choices(question):
    '''
     @return: choices for a given select type question
     TODO: What might this be used for (so the reviewer doesn't have to go searching)
    '''
    choices_list = question.selectoptions
    
    if choices_list == None:
        return None
    choices= [(x,x) for x in choices_list]
    return choices
    
def generate_charfield():
    '''
     @return charfield ,you can change the default attribute TODO: what does this mean?
     TODO: document the default attributes that you have set (e.g. what makes this different from any other charfield)
    '''
    return CharField(max_length=100,widget=forms.TextInput(attrs={'size':'40'}))

def generate_textfield():
    '''
     @return textfield ,you can define the default attribute TODO: what does this mean?
     TODO: document the default attributes that you have set (e.g. what makes this different from any other charfield)
    '''    
    return CharField(widget = forms.Textarea(attrs={'rows':'4','cols':'40',}))

def generate_boolean_field():
    '''
     @return Boolean field   
     initial value set to True and required =False to allow dynamic change of value to etheir False or True
    '''   
    return TypedChoiceField(
                         choices=((1,'Yes'),(0,'No')), 
                         widget=forms.RadioSelect, coerce=int
                    ) 
    

def generate_select_dropdown_field():
    '''
    @return: return form ChoiceField
    TODO: document the default attributes that you have set (e.g. what makes this different from any other Choicefield)
    '''
    return ChoiceField(choices=[])

def generate_radioselect_field():
    '''
    @return radioselect field no default set TODO: this isn't actually true, it returns a ChoiceField that has a RadioSelect widget
    ''' 
    return ChoiceField(widget=RadioSelect,choices=[])

def generate_multiplechoice_field():
    '''
    @return MultipleChoiceField
    TODO: document the default attributes that you have set (e.g. what makes this different from any other MultipleChoiceField)
    '''
    return MultipleChoiceField(choices=[], widget=forms.CheckboxSelectMultiple(),error_messages={'required': 'This question is required can not be empty select one or more answer '})


#TODO: document what this this dictionary used for
FIELD_TYPES={
            'charfield': generate_charfield ,
            'textfield': generate_textfield,
            'booleanfield': generate_boolean_field,
            'select_dropdown_field':generate_select_dropdown_field,
            'radioselectfield':generate_radioselect_field,
            'multiplechoicefield':generate_multiplechoice_field,
            }

def _get_fields_for_group(questiongroup):
    '''
        This builds a sorted dict of fields that are created in the order defined in the 
        questiongroup, and created based on the question label and the question type
    '''
    questions = questiongroup.get_ordered_questions()
        
    fields = []
    
    for question in questions:
        
        field = FIELD_TYPES[question.field_type]()
        field.label = question.label
        choices = get_choices(question)
        if choices != None:
            field.choices= choices
        fields.append((str(question.id),field))
    return fields

def _convert_answerset_to_intial_data(answer_set):
    '''
        This function takes an asnwer set and then returns the QuestionAnswers as a dictionary
        suitable to be used as the intial data for a form
    '''
    if not isinstance(answer_set, AnswerSet):
        raise AttributeError('This function only accepts an AnswerSet asn its argument')
    initial_data = {}
    for question_answer in answer_set.get_latest_question_answers():
        initial_data[str(question_answer.question.id)] = question_answer.answer
    return initial_data
    

class QuestionGroupForm(forms.Form):
    '''
        This form will be used to render the form for each question group
        by passing a questiongroup into the constructor it will dynamically generate
        the form fields required to render and validate the questions in any question group
    '''
    def __init__(self, questiongroup, initial=None, data=None):
        if isinstance(initial, AnswerSet):
            initial = _convert_answerset_to_intial_data(initial)
        
        super(QuestionGroupForm, self).__init__(initial=initial, data = data)
        
        
        
        for field in _get_fields_for_group(questiongroup):
            
            self.fields[field[0]] = field[1]

         
            
        
        


        
