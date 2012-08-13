'''
Created on Jul 10, 2012

@author: mzd2
@author: ayoola
'''
from django.db import models

from django.contrib.auth.models import User


class CustomListField(models.TextField):
    '''
    for creating  custom list field override some model.fields methods
    '''
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
    
        kwargs={'default':None,'null':True,'blank':True,
                'help_text':'Enter option for select Field Type seperated by comma e.g No ,Yes,Not Applicable . TO EDIT EXISTING OPTIONS CLEAR THE OPTIONS AND TYPE AFRESH '}
        
        super(CustomListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        '''
        @return: list if it exist 
        '''
        if not value: return
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

    #def value_to_string(self, obj):
       # value = self._get_val_from_obj(obj)
       # return self.get_db_prep_value(value) 

     
FIELD_TYPE_CHOICES=(('charfield','charfield'),('textfield','textfield'),('booleanfield','boolean'),('select_dropdown_field','select_dropdown_field'),('radioselectfield','radioselectfield'),('multiplechoicefield','multiplechoicefield'))
    
class Question(models.Model):
    '''
    responsible for storing questions
    define attributes of a question and type of questions e.g boolean ,textfield , charfield
    '''
    class Meta():
        db_table ='question'
    
    label=models.CharField('question',max_length=255)
    field_type=models.CharField(choices=FIELD_TYPE_CHOICES,max_length=100)    
    selectoptions=CustomListField()

    def __unicode__(self):
        return 'Question:%s FieldType:%s Selectoptions:%s' %(self.label, self.field_type,str(self.selectoptions))
    
    def save(self,*args,**kwgs):
        if not self.id:
            if not self.field_type in ['select_dropdown_field','radioselectfield', 'multiplechoicefield'] :              
                self.selectoptions = None
            
            
        super(Question,self).save(*args,**kwgs)

    
class QuestionGroup(models.Model):
    '''
    reponsible for question groups ,each group set can have one to  many set of questions 
    order_no store the order or sequence the question group is to be rendered .e.g  order_no = 2 will be rendered before order_no =3  
    '''
    class Meta():
        db_table ='questiongroup'
    name = models.CharField('questiongroupname',max_length=255,unique=True)
    questions = models.ManyToManyField(Question, through = 'Question_order')
    
    def get_ordered_questions(self):
        return [order.question for order in Question_order.objects.filter(questiongroup=self).order_by('order_info')]
    
    def __unicode__(self):
        return self.name
   
class Questionnaire(models.Model):
    '''
    This class stores the Questionnaire name
    '''
    name=models.CharField(max_length=250)
    questiongroup=models.ManyToManyField(QuestionGroup, through='QuestionGroup_order')
    
    def get_ordered_groups(self):
        return QuestionGroup_order.objects.filter(questionnaire=self).order_by('order_info')
    
    def __unicode__(self):
        return self.name
    
class QuestionGroup_order(models.Model):
    '''
    This class stores the ordering of the question rendered on the page
    '''
    questiongroup=models.ForeignKey(QuestionGroup)
    questionnaire=models.ForeignKey(Questionnaire)
    order_info=models.IntegerField(max_length=3)
    
    def __unicode__(self):
        return 'group:%s order:%s' %(self.questiongroup, str(self.order_info))
    
    
class Question_order(models.Model):
    '''
    This class is responsible in storing the ordering relation ship between the question and questiongroup
    '''
    questiongroup =models.ForeignKey(QuestionGroup)
    question = models.ForeignKey(Question)
    order_info = models.IntegerField(max_length=3)
    
    def __unicode__(self):
        return 'group:%s order:%s' %(self.question, str(self.order_info))
    
    
        
class AnswerSet(models.Model):
    '''
    this class datamodel for storing users and questionnaire

    '''
    class Meta():
        db_table ='answer_set'
    user=models.ForeignKey(User)
    questionnaire=models.ForeignKey(Questionnaire)
    questiongroup=models.ForeignKey(QuestionGroup)
    
    def save(self, *args, **kwargs):                       
        super(AnswerSet, self).save(*args, **kwargs)
        
    def __unicode__(self):
        return 'user:%s questionnaire:%s  questiongroup:%s ' %(str(self.user), str(self.questionnaire),str(self.questiongroup)) 
        
class QuestionAnswer(models.Model):    
    '''
    This model is used to store reusable question, answer and answer_set
    '''
    class Meta():
        db_table ='questionanswer'
        
    question = models.ForeignKey(Question)
    answer = models.CharField(max_length=255)
    answer_set = models.ForeignKey(AnswerSet)
    
    def save(self, *args, **kwargs):                       
        super(QuestionAnswer, self).save(*args, **kwargs)  
    
    def __unicode__(self):
        return 'question:%s answer:%s answer_set:%s' %(str(self.question), str(self.answer), str(self.answer_set))
