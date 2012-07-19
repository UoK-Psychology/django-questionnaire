'''
Created on Jun 26, 2012

@author: ayoola_al

'''

from django import forms
from models import QuestionGroup
from django.forms.fields import CharField,BooleanField,ChoiceField,MultipleChoiceField
from django.forms.widgets import RadioSelect ,CheckboxSelectMultiple
from django.utils.datastructures import SortedDict

class CustomError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def get_choices(question):
    '''
     @return: choices for a given select type question
    '''
    try: 
        choices_list = question.selectoptions
        choices= [(x,x) for x in choices_list]
        return choices
    except CustomError as e:
         msg='Exception has occurred not a valid List : s%' % e.value
         raise MyError(msg)

def generate_charfield():
    '''
     @return charfield ,you can change the default attribute
    '''
    return CharField(max_length=100,widget=forms.TextInput(attrs={'size':'40'}))

def generate_textfield():
    return CharField(widget = forms.Textarea(attrs={'rows':'4','cols':'40',}))

def generate_boolean_field():
    return BooleanField(initial= False)

def generate_select_dropdown_field():
    '''
    @return: return form ChoiceField
     
    '''
    return ChoiceField(choices=[])

def generate_radioselect_field():
    '''
    @return radioselect field no default set
    ''' 
    return ChoiceField(widget=RadioSelect,choices=[])
def generate_multiplechoice_field():
    '''
    @return MultipleChoiceField
    '''
    return MultipleChoiceField(choices=[], widget=forms.CheckboxSelectMultiple())



FIELD_TYPES={
            'charfield': generate_charfield ,
            'textfield': generate_textfield,
            'booleanfield': generate_boolean_field,
            'select_dropdown_field':generate_select_dropdown_field,
            'radioselectfield':generate_radioselect_field,
            'multiplechoicefield':generate_multiplechoice_field,
            }

def make_question_group_form(questiongroup_id,questionnaire_id):
    '''
     mapping questions fields  type  to form fields type 
     @return: type form for specific questiongroup 
    
    '''
    fields = SortedDict([])
    
    #thisgroupquestions = QuestionGroup.objects.get(id=questiongroup_id).questions.all()
    
    
    group = QuestionGroup.objects.get(pk=questiongroup_id)
    orderedgroups = group.get_ordered_groups()

    #below prints the questiongroup id! so it can be used to render a group!

    
    for question in orderedgroups:
        
        if question.question.field_type == 'select_dropdown_field' or question.question.field_type == 'radioselectfield' or question.question.field_type =='multiplechoicefield':
            tempfield=FIELD_TYPES[question.question.field_type]()
            tempfield.choices=get_choices(question.question)
            field=tempfield
            field.label = question.question.label
            fields[str(question.question.id)]= field
        else:    
            field = FIELD_TYPES[question.question.field_type]()
            field.label = question.question.label
            fields[str(question.question.id)]= field
            
    return type('%sForm' % id (questionnaire_id),(forms.BaseForm,),{'base_fields':fields})


  
            