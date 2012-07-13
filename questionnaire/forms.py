'''
Created on Jun 26, 2012

@author: ayoola_al

'''

from django import forms
from models import QuestionGroup
from django.forms.fields import CharField,BooleanField, ChoiceField

def get_choices(question):
    choices_list=question.selectoptions
    choices= [(x,x) for x in choices_list]
    return choices
 
def generate_charfield():
    return CharField(max_length=100)

def generate_textfield():
    return CharField(widget = forms.Textarea)

def generate_boolean_field():
    return BooleanField(initial= False)

def generate_selectfield_field():
    return ChoiceField(choices=[])

FIELD_TYPES={
            'charfield': generate_charfield ,
            'textfield': generate_textfield,
            'booleanfield': generate_boolean_field,
            'selectfield':generate_selectfield_field,
            }

def make_question_group_form(questiongroup_id):
    '''
     mapping questions fields  type  to form fields type 
     @return: type form for specific questiongroup 
    
    '''
    fields={}
    thisgroupquestions = QuestionGroup.objects.get(id=questiongroup_id).questions.all()
    
    
    Group = QuestionGroup.objects.get(pk=questiongroup_id)
    orderedgroups = Group.get_ordered_groups()
    
    print thisgroupquestions
    print orderedgroups
    

        
    
    
    #below prints the questiongroup id! so it can be used to render a group!

    
    for question in orderedgroups:
        
        if question.question.field_type == 'selectfield':
            tempfield=FIELD_TYPES[question.question.field_type]()
            tempfield.choices=get_choices(question.question)
            field=tempfield
            field.label = question.question.label
            fields[int(question.question.id)]= field
        else:    
            field = FIELD_TYPES[question.question.field_type]()
            field.label = question.question.label
            fields[int(question.question.id)]= field
            
    return type('QuestionForm',(forms.BaseForm,),{'base_fields':fields})


  
            