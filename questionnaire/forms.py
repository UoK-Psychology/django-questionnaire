'''
Created on Jun 26, 2012

@author: ayoola_al

'''

from django import forms
from models import QuestionAnswer
from django.forms.fields import CharField,BooleanField,ChoiceField,MultipleChoiceField
from django.forms.widgets import RadioSelect 
from django.utils.datastructures import SortedDict
from django.db.models import Q
from django.db.models import Max

  


def get_choices(question):
    '''
     @return: choices for a given select type question
    '''
    choices_list = question.selectoptions
    choices= [(x,x) for x in choices_list]
    return choices
    
def generate_charfield():
    '''
     @return charfield ,you can change the default attribute
    '''
    return CharField(max_length=100,widget=forms.TextInput(attrs={'size':'40'}))

def generate_textfield():
    '''
     @return textfield ,you can define the default attribute 
    '''    
    return CharField(widget = forms.Textarea(attrs={'rows':'4','cols':'40',}))

def generate_boolean_field():
    '''
     @return Boolean field   
     initial value set to True and required =False to allow dynamic change of value to etheir False or True
    '''    
    return BooleanField(required=False ,initial=True)

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
    return MultipleChoiceField(choices=[], widget=forms.CheckboxSelectMultiple(),error_messages={'required': 'This question is required can not be empty select one or more answer '})



FIELD_TYPES={
            'charfield': generate_charfield ,
            'textfield': generate_textfield,
            'booleanfield': generate_boolean_field,
            'select_dropdown_field':generate_select_dropdown_field,
            'radioselectfield':generate_radioselect_field,
            'multiplechoicefield':generate_multiplechoice_field,
            }

def make_question_group_form(questiongroup,questionnaire_id):
    '''
     mapping questions fields  type  to form fields type 
     @return: type form for specific questiongroup 
    
    '''
    fields = SortedDict([])
       
    
    orderedgroups = questiongroup.get_ordered_questions()
    
    
    for question in orderedgroups:
        

        if question.field_type in ['select_dropdown_field','radioselectfield','multiplechoicefield']:
            field=FIELD_TYPES[question.field_type]()
            if get_choices(question):
                field.choices=get_choices(question)
            
            field.label = question.label
            fields[str(question.id)]= field
        else:    
            field = FIELD_TYPES[question.field_type]()
            field.label = question.label
            fields[str(question.id)]= field

            
    return type('%sForm' % id (questionnaire_id),(forms.BaseForm,),{'base_fields':fields})



def  create_question_answer_edit_form(user,this_questionnaire,this_questiongroup):
    '''
    create form for editing recent question answer for given user 
    prepopulate fields with most recent answers for given user and questiongroup
    field.initial store  most recent answers to prepopulate the form fields 
    '''  
    q_list=QuestionAnswer.objects.values('question','answer_set').annotate(Max('id'))
    answer_max_id_list=q_list.values_list('id__max',flat=True)
    qs=QuestionAnswer.objects.filter(Q(answer_set__user_id=user,answer_set__questiongroup=this_questiongroup,answer_set__questionnaire=this_questionnaire)).filter(id__in=answer_max_id_list)  
    questionanswer=[(x.question ,x.answer) for x in qs] 

    fields = SortedDict([])
    for (question,answer)in questionanswer:
        
        if  question.field_type in ['select_dropdown_field','radioselectfield','multiplechoicefield']:
            field=FIELD_TYPES[question.field_type]()
            field.label= question.label
            field.choices=get_choices(question)
            
            if question.field_type == 'multiplechoicefield':
                field.initial = [str(x) for x in answer.split(',')]
            else:
                field.initial=str(answer)
                
            fields[str(question.id)]= field
        else:
            field=FIELD_TYPES[question.field_type]()
            field.label= question.label
            
            if not question.field_type =='booleanfield':
                field.initial = answer
                
            fields[str(question.id)]= field
             
    return type('editForm',(forms.BaseForm,),{'base_fields':fields})
        

     
   
        
