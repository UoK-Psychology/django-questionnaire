'''
Created on Jul 10, 2012

@author: mzd2
'''
from django.db import models

from django.contrib.auth.models import User

 


FIELD_TYPE_CHOICES=((0,'charfield'),(1,'textfield'),(2,'boolean'), (3,'select'))
    
class Question(models.Model):
    '''
    responsible for storing questions
    define attributes of a question and type of questions e.g boolean ,textfield , charfield
    '''
    class Meta():
        db_table ='question'
    
    label=models.CharField('question',max_length=255)
    field_type=models.IntegerField(choices=FIELD_TYPE_CHOICES)
    
    
    def __unicode__(self):
        return self.label
    
class Questiongroup(models.Model):
    '''
    reponsible for question groups ,each group set can have one to  many set of questions 
    order_no store the order or sequence the question group is to be rendered .e.g  order_no = 2 will be rendered before order_no =3  
    '''
    class Meta():
        db_table ='questiongroup'
    name = models.CharField('questiongroupname',max_length=255,unique=True)
    questions = models.ManyToManyField(Question, through = 'Question_order')
    
    def __unicode__(self):
        return self.name
   
class Questionnaire(models.Model):
    '''
    This class stores the Questionnaire name
    '''
    name=models.CharField(max_length=250)
    questiongroup=models.ManyToManyField(Questiongroup, through='QuestionGroup_order')
    
    def __unicode__(self):
        return self.name
    
class QuestionGroup_order(models.Model):
    '''
    This class stores the ordering of the question rendered on the page
    '''
    questiongroup=models.ForeignKey(Questiongroup)
    questionnaire=models.ForeignKey(Questionnaire)
    order_info=models.IntegerField(max_length=3)
    
    def __unicode__(self):
        return 'group:%s order:%s' %(self.questiongroup, str(self.order_info))
    
    
class Question_order(models.Model):
    '''
    This class is responsible in storing the ordering relation ship between the question and questiongroup
    '''
    questiongroup =models.ForeignKey(Questiongroup)
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
    
    
    
    def save(self, *args, **kwargs):                       
        super(AnswerSet, self).save(*args, **kwargs)    
        
class QuestionAnswer(models.Model):    
    '''
    This model is used to store reusable question, answer and answer_set
    '''
    question = models.ForeignKey(Question)
    answer = models.CharField(max_length=255)
    answer_set = models.ForeignKey(AnswerSet)
    
