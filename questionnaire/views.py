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
    
    
    
    
    if request.method =='POST':
        request.POST
        print request.POST
        form = questionForm(request.POST)

        
        if form.is_valid():
            a = form.cleaned_data
            print a
        

        
        
    
        
        if order_info == orderedgroups.count():
            this = 'this is the last one!'
            print this
            return HttpResponseRedirect(reverse('questionnaire_finish'))
            
        else:
            
            this = 'Continue! pass order_info+1 !'
            print this
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
        print self.cleaned_data.items()
        yield (question, answer)    

def display_question_answer(request,questionnaire_id):
    if request.method=='GET':
        user=request.user
        questionanswer=QuestionAnswer.objects.values()
        
        paginator = Paginator(questionanswer, 2)  
        context=questionanswer
    return render_to_response('questionanswer.html',{'context':context,},context_instance=RequestContext(request))


def get_next_questiongroupid(this_questionnaire):
    '''
     retrieve ordered groups for given questionnaire ordered by order_info put them in a list
     generator return next questiogroup
     for example
     orderedgroups =[{'questionnaire_id': 1, 'id': 1, 'order_info': 1, 'questiongroup_id': 10},
     {'questionnaire_id': 1, 'id': 2, 'order_info': 3, 'questiongroup_id': 11}]
     orderlist = [10, 11]
     @return: next questiongroup_id
    '''
    orderedgroups = QuestionGroup_order.objects.filter(questionnaire= this_questionnaire).order_by('order_info').values()
    orderlist=([ordergroup['questiongroup_id'] for ordergroup in orderedgroups])
    for i, group_id in enumerate(orderlist):
        yield  group_id
    
    
def get_total_group_questions(questiongroup_id):
    '''
    @return: total number of questions in the given questiongroup
    '''
    totalcount =  QuestionGroup.objects.get(pk=questiongroup_id).questions.all().count()
    return totalcount


def get_questionnnaire_obj(questionnaire_id):
    '''
    @return: questionnaire instance
    '''
    thisquestionnaire=get_object_or_404(Questionnaire,pk=questionnaire_id)
    
    return thisquestionnaire

def get_questionnnaire_name(questionnaire_id):
    '''
    @return: questionnaire name
    '''
    thisquestionnaire=get_object_or_404(Questionnaire,pk=questionnaire_id)
    
    return thisquestionnaire.name

def get_question_obj(question_id):
    '''
    @return: question object instance
    '''
    thisquestion=get_object_or_404(Question,pk=question_id)
    
    return thisquestion

def get_question_name(question_id):
    '''
    @return: question this question label actual question
    '''
    thisquestion=get_object_or_404(Question,pk=question_id)
    
    return thisquestion.label