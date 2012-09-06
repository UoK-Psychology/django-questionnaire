'''
Created on Jun 26, 2012

@author: ayoola_al

'''

from django import forms
from models import QuestionAnswer
from django.forms.fields import CharField,BooleanField,ChoiceField,MultipleChoiceField
from django.forms.widgets import RadioSelect , HiddenInput
from django.utils.datastructures import SortedDict
from django.db.models import Q
from django.db.models import Max
from django.forms.forms import BaseForm

  


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
    return BooleanField(required=False ,initial=True)

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
        field.choices=get_choices(question)
        fields.append((str(question.id),field))
    return fields


class QuestionGroupForm(forms.Form):
    
    
    questionnaire_id = CharField(widget=HiddenInput)
    
    def __init__(self, questiongroup, questionnaire_id, initial=None, data=None):
        
        super(QuestionGroupForm, self).__init__()
        
        
        
        for field in _get_fields_for_group(questiongroup):
            
            self.fields[field[0]] = field[1]
            
        self.initial = initial or {}
        self.data = data or {}
        
        self.data['questionnaire_id'] = questionnaire_id

         
            
        
        

def make_question_group_form(questiongroup,questionnaire_id):
    '''
     mapping questions fields  type  to form fields type 
     @return: type form for specific questiongroup 
    
    '''
    fields = SortedDict([])#TODO: document why you are using a sortedict
       
    
    orderedgroups = questiongroup.get_ordered_questions()
    
    
    for question in orderedgroups:
        

        if question.field_type in ['select_dropdown_field','radioselectfield','multiplechoicefield']:
            field=FIELD_TYPES[question.field_type]()
            if get_choices(question):#TODO: do we really need to do this if this function returns None, then you might as well set field.choices=None as it will be None anyway?
                field.choices=get_choices(question)
            
            field.label = question.label
            fields[str(question.id)]= field
        else:    
            field = FIELD_TYPES[question.field_type]()
            field.label = question.label
            fields[str(question.id)]= field

    #TODO: it might be worth explaining this a bit more as this is quite advanced python and might not be totally clear to the reviewer
    return type('%sForm' % id (questionnaire_id),(forms.BaseForm,),{'base_fields':fields})



def  create_question_answer_edit_form(user,this_questionnaire,this_questiongroup):
    '''
    create form for editing recent question answer for given user 
    prepopulate fields with most recent answers for given user and questiongroup
    field.initial store  most recent answers to prepopulate the form fields 
    '''  
    
    #TODO: this block looks very similar to the one used in the view code - consider refactoring this to a function, perhaps located as a function of QuestionGroup i.e. get_questionsanswers_for_user or something like that?
    q_list=QuestionAnswer.objects.values('question','answer_set').annotate(Max('id'))
    answer_max_id_list=q_list.values_list('id__max',flat=True)
    qs=QuestionAnswer.objects.filter(Q(answer_set__user_id=user,answer_set__questiongroup=this_questiongroup,answer_set__questionnaire=this_questionnaire)).filter(id__in=answer_max_id_list)  
    questionanswer=[(x.question ,x.answer) for x in qs] 

    fields = SortedDict([])
    
    #TODO:This block appears to be very similar to make_question_group_form consider refactoring the shaared code into a function that can be used by both form functions.
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
        

     
   
        
