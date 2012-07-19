from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from models import QuestionGroup_order, Questionnaire,QuestionGroup,AnswerSet,QuestionAnswer,Question
from django.template import  RequestContext
from django.shortcuts import render_to_response
from questionnaire.forms import make_question_group_form
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import get_object_or_404

from django.contrib.auth.models import  User
from django.contrib.auth.decorators import login_required

def index (request):
    return HttpResponseRedirect(reverse('index'))


def get_next_questiongroup(request,questionnaire_id,order_info=None):
    questionnaire_id = int(questionnaire_id)
    if order_info==None:
        order_info = 1

    else:
        order_info = int(order_info)
        
    quest = Questionnaire.objects.get(pk=questionnaire_id)
    orderedgroups = quest.get_ordered_groups()
    
    #below prints the questiongroup id! so it can be used to render a group!
    questiongroup_id = orderedgroups[order_info-1].questiongroup.id    
    
    questionForm = make_question_group_form(questiongroup_id,questionnaire_id)
    
    
    this_questionnaire= get_questionnnaire_obj(questionnaire_id)
    
    if request.method =='POST':
        
        form=questionForm(request.POST)
        if form.is_valid():
            
            this_answer_set, created = AnswerSet.objects.get_or_create(user=request.user,questionnaire=this_questionnaire)
            
            #this_answer_set= AnswerSet(user=request.user,questionnaire=this_questionnaire)
            #this_answer_set.save()
            
            
            
            formdata=get_answers(form)     
            for question,answer in formdata:
                this_question_answer=QuestionAnswer(question=get_question_obj(question),answer=str(answer),answer_set=this_answer_set)
                this_question_answer.save()
            
            if order_info >= orderedgroups.count():
                return HttpResponseRedirect(reverse('questionnaire_finish'))
            
            else: 
                order_info = order_info + 1
                return HttpResponseRedirect(reverse('get_next_questiongroup', kwargs = {'questionnaire_id': questionnaire_id, 'order_info' : order_info}))
    
    else:
        return render_to_response('questionform.html', 
        {'form': questionForm,},context_instance=RequestContext(request))
    



def finish(request):
    return render_to_response('finish.html')     
     

def get_answers(self):
    '''
    return question and answer pair tuple
    
    self.field[name].label is data for the object to be inserted to the QuestionAnswer
    '''  
    for question, answer in self.cleaned_data.items():
        
        yield (question, answer)    

def display_question_answer(request,questionnaire_id):
    if request.method=='GET':
        user=request.user
        questionanswer=QuestionAnswer.objects.values()   
        questionanswer2 = QuestionAnswer.objects.all()
        
        answerset = AnswerSet.objects.values() 
        answerset2 = AnswerSet.objects.all()
        
        
        context=questionanswer        
    return render_to_response('questionanswer.html',{'context':context,},context_instance=RequestContext(request))



def get_questionnnaire_obj(questionnaire_id):
    '''
    @return: questionnaire instance
    '''
    thisquestionnaire=get_object_or_404(Questionnaire,pk=questionnaire_id)
    
    return thisquestionnaire

def get_question_obj(question_id):
    '''
    @return: question object instance
    '''
    thisquestion=get_object_or_404(Question,pk=question_id)
    
    return thisquestion

