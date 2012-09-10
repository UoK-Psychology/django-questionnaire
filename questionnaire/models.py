'''
Created on Jul 10, 2012

@author: mzd2
@author: ayoola
'''
from django.db import models

from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ObjectDoesNotExist


class CustomListField(models.TextField):
    '''
    for creating  custom list field override some model.fields methods
    TODO: improve the description of what this is, and why you would want to use it
    '''
    __metaclass__ = models.SubfieldBase#TODO: document what the significance of this is

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
    
        kwargs={'default':None,'null':True,'blank':True,
                'help_text':'Enter option for select Field Type seperated by comma e.g No ,Yes,Not Applicable . TO EDIT EXISTING OPTIONS CLEAR THE OPTIONS AND TYPE AFRESH '}
        
        super(CustomListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        '''
        @return: list if it exist 
        TODO:consider imporoving this to give more detail, ie what do you pass in to value and how does the conversion to list happen?
        '''
        if not value: return #TODO: is this the same as return None?
        if isinstance(value, list):
            return value
        return value.split(self.token)

    def get_db_prep_value(self, value,connection=None,prepared=False):
        '''
        @return string separated by token as stored in database
        '''
        if not value: return
        assert(isinstance(value, list) or isinstance(value, tuple))
        return self.token.join([unicode(s) for s in value])

#TODO: what is this tuple used for?
FIELD_TYPE_CHOICES=(('charfield','charfield'),('textfield','textfield'),('booleanfield','boolean'),('select_dropdown_field','select_dropdown_field'),('radioselectfield','radioselectfield'),('multiplechoicefield','multiplechoicefield'))
    
class Question(models.Model):
    '''
    model question objects attributes
    define attributes of a question:
    1.label : the actual question  eg what is your name?
    2.field_type: type of questions or type of answers you expect or require for the question e.g 
        booleanfield -if answer require is True or False
        charfield-if answer require typing some info in a form field 
        textfield- if answer require typing more detail info in a form text field 
        select_dropdown_field- if answer require selecting one answer from some options 
        multiplechoicefield-if answer require selecting one or more answer from some options
        radioselectfield-if answer require selecting only one answer from some options 
    3.selectoptions :list of choices or options available for  question .Required for field type is choicefields i.e select_dropdown_field,radioselectfield, multiplechoicefield
                     otherwise selectoptions is None .options stored as comma ","seperarted strings
                     e.g selectoptions for a question of field_type-radioselectfield may be 'Yes',' No' ,'Not Applicable'
    
    '''
    class Meta():
        db_table ='question'
    
    label=models.CharField('question',max_length=255)
    field_type=models.CharField(choices=FIELD_TYPE_CHOICES,max_length=100)    
    selectoptions=CustomListField()

    def __unicode__(self):
        return 'Question:%s FieldType:%s Selectoptions:%s' %(self.label, self.field_type,str(self.selectoptions))
    
    def save(self,*args,**kwgs):
        '''
          ensure selectoption for non choicefield is saved as None 
          only choicefields require selectoptions i.e select_dropdown_field,radioselectfield, multiplechoicefield should have options 
        '''
        if not self.id:
            if not self.field_type in ['select_dropdown_field','radioselectfield', 'multiplechoicefield'] :              
                self.selectoptions = None
            
        super(Question,self).save(*args,**kwgs)

#TODO: Move this to forms.py
class CustomListWidget(forms.Textarea):
    '''
    create flatten custom widget use to render CustomList Field 
    displays selectoptions List as string of strings  separated by comma 
    e.g customList field [A,B,C] will be displayed and stored as A,B,C string
    '''
    def render(self, name, value, attrs=None):
        if  value :
            value = ','.join(str(v) for v in value)
        return super(CustomListWidget, self).render(name, value, attrs)

#TODO: move this to forms.py
class QuestionAdminForm(forms.ModelForm):
    '''
    overide admin form validation for  Question selectoptions attribute 
    ensure user enter valid selectionoptions/choices for all  field types 
    1.check selectoptions field for choicefield i.e multiplechoice ,radioselectfield and select_dropdown_field field_type 
    is not empty and are   ","  separated string
    2.check the selectioptions for Non choice field types are None or Empty i.e charfield,textfield ,booleanfield 
    if error appropriate error message will be displayed
    Questions are reuseable
    '''
    class Meta:
        model = Question
        widgets = {'selectoptions': CustomListWidget(),}

    def clean(self):
        '''
        custom clean for select options validation
        @return: cleaned_data
        
        '''
        field_type=self.cleaned_data["field_type"]
        selectoptions = self.cleaned_data["selectoptions"]
        
        if field_type  in ['select_dropdown_field','radioselectfield', 'multiplechoicefield'] : 
            
            if  not selectoptions:
                raise forms.ValidationError("Select Options is required for "+ str(field_type)+ " enter valid options seperated with commas e.g No,Yes,Not Applicable")        
          
            elif  ","  not in  selectoptions :
                raise forms.ValidationError("Enter valid options seperated with comma e.g No,Yes,Not Applicable")
                
        elif field_type in ['charfield','textfield','booleanfield']:
            if selectoptions :
                raise forms.ValidationError("Select Options is not required  for " + str(field_type) + " Must Be Left Empty")
        
        return self.cleaned_data

    
class QuestionGroup(models.Model):
    '''
    reponsible for question groups ,each group set can have one to  many set of questions 
    order_info store the order or sequence the question group is to be rendered in a form .e.g  order_info = 2 will be rendered before order_info =3  
    '''
    class Meta():
        db_table ='questiongroup'
        
    name = models.CharField('questiongroupname',max_length=255,unique=True)
    questions = models.ManyToManyField(Question, through = 'Question_order')
    
    def get_ordered_questions(self):
        '''
        @return: questions in  question group ordered by order_info
        '''
        return [order.question for order in Question_order.objects.filter(questiongroup=self).order_by('order_info')]
    
    def __unicode__(self):
        return self.name
   
class Questionnaire(models.Model):
    '''
    This class models the Questionnaire and its attributes
    name : name for the questionnaire 
    questiongroups: the question groups in the named questionnaire
    questiongroups are reuseable i.e a given questiongroup can be reused in one or more questionnaire  
     
    '''
    name=models.CharField(max_length=250)
    questiongroup=models.ManyToManyField(QuestionGroup, through='QuestionGroup_order')
    
    def get_ordered_groups(self):
        '''
        @return: the questiongroups in a questionnaire order by the order_info
            
        '''
        return QuestionGroup_order.objects.filter(questionnaire=self).order_by('order_info')
    
    def get_group_for_index(self, index):
        '''
            Returns the question group that is at the position in the ordered sequence of groups
            represented by the index argument
            
            If there is not a group at this index in the ordered_groups then an index error will be thrown.
        '''
        ordered_groups = [order_info.questiongroup for order_info in self.get_ordered_groups()]
        return (ordered_groups[index], (len(ordered_groups) - index) -1)
    
    
    def __unicode__(self):
        return self.name
    
class QuestionGroup_order(models.Model):
    '''
    This class stores the ordering of the questiongroups rendered in a questinnaire
    order_info store the order or sequence the questiongroup is to be rendered in a form .e.g  order_info = 2 will be rendered before order_info =3  
    '''
    questiongroup=models.ForeignKey(QuestionGroup)
    questionnaire=models.ForeignKey(Questionnaire)
    order_info=models.IntegerField(max_length=3)
    
    def __unicode__(self):
        return 'group:%s order:%s' %(self.questiongroup, str(self.order_info))
    
    
class Question_order(models.Model):
    '''
    This class is responsible in storing the ordering relationship between the question and questiongroup
    order_info store the order or sequence the questions in a questiongroup is to be rendered in a form .e.g  order_info = 2 will be rendered before order_info =3  
    '''
    questiongroup =models.ForeignKey(QuestionGroup)
    question = models.ForeignKey(Question)
    order_info = models.IntegerField(max_length=3)
    
    def __unicode__(self):
        return 'group:%s order:%s' %(self.question, str(self.order_info))
    
    
        
class AnswerSet(models.Model):
    '''
  model store relationship for users answer for  questiongroup in a questionnaire
  associates a user to a questiongroup in a questionnaire when answers the questionnaire

    '''
    class Meta():
        db_table ='answer_set'
        
    user=models.ForeignKey(User)
    questionnaire=models.ForeignKey(Questionnaire)
    questiongroup=models.ForeignKey(QuestionGroup)
        
    def __unicode__(self):
        return 'user:%s questionnaire:%s  questiongroup:%s ' %(str(self.user), str(self.questionnaire),str(self.questiongroup)) 
    
    def get_latest_question_answers(self):
        '''
            Convenience function that returns a list of the latest QuestionAnswer objects (bearing in mind that you could
            have more than one QuestionAnswer for each question in a given answer set).
        '''
        return [record.question_answer for record in LatestQuestionAnswer.objects.filter(answer_set=self)]  
     
class QuestionAnswer(models.Model):    
    '''
    This model stores questions, answers and related answer_set 
    '''
    class Meta():
        db_table ='questionanswer'
        
    question = models.ForeignKey(Question)
    answer = models.CharField(max_length=255)
    answer_set = models.ForeignKey(AnswerSet)
    created = models.DateTimeField(auto_now_add=True)
     
    
    def save(self, force_insert=False, force_update=False, using=None):
        super(QuestionAnswer, self).save(force_insert=force_insert, force_update=force_update, using=using)
        #now update the LatestQuestionAnswer table
        
        try:
            record = LatestQuestionAnswer.objects.get(question=self.question, answer_set=self.answer_set)
            
            if record.question_answer == self:
                return#nothing to do no point updating the record as it is already correct
            
        except ObjectDoesNotExist:
            record = LatestQuestionAnswer(question=self.question, answer_set= self.answer_set)
            
        record.question_answer = self
        record.save()
    
    def __unicode__(self):
        return 'question:%s answer:%s answer_set:%s' %(str(self.question), str(self.answer), str(self.answer_set))

class LatestQuestionAnswer(models.Model):
    question = models.ForeignKey(Question)
    question_answer = models.ForeignKey(QuestionAnswer)
    answer_set = models.ForeignKey(AnswerSet)
    created = created = models.DateTimeField(auto_now_add=True)