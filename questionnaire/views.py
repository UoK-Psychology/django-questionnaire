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

@login_required
def handle_next_questiongroup_form(request,questionnaire_id,order_info=None):
    questionnaire_id = int(questionnaire_id)
    if order_info==None:
        order_info = 1

    else:
        order_info = int(order_info)
        
    this_questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_id)
    orderedgroups = this_questionnaire.get_ordered_groups()
    
    questiongroup = orderedgroups[order_info-1].questiongroup    
    
    questionForm = make_question_group_form(questiongroup,questionnaire_id)
    
    
    
    
    if request.method =='POST':
        
        form=questionForm(request.POST)
        if form.is_valid():
            
            this_answer_set, created = AnswerSet.objects.get_or_create(user=request.user,questionnaire=this_questionnaire)
    
   
            for question, answer in form.cleaned_data.items():
                
                this_question_answer, create = QuestionAnswer.objects.get_or_create(question= get_object_or_404(Question, pk=question),answer=str(answer),answer_set=this_answer_set)
                
                
            if order_info >= orderedgroups.count():
                return HttpResponseRedirect(reverse('questionnaire_finish'))
            
            else: 
                order_info = order_info + 1
                return HttpResponseRedirect(reverse('handle_next_questiongroup_form', kwargs = {'questionnaire_id': questionnaire_id, 'order_info' : order_info}))
    
    else:
        return render_to_response('questionform.html', 
        {'form': questionForm,},context_instance=RequestContext(request))
    
        


def finish(request):
    return render_to_response('finish.html')     
      
@login_required
def display_question_answer(request,questionnaire_id):
    if request.method=='GET':
        user=request.user
        questionanswer=QuestionAnswer.objects.values()   
        questionanswer2 = QuestionAnswer.objects.all()
        
        answerset = AnswerSet.objects.values() 
        answerset2 = AnswerSet.objects.all()
        
        
        context=questionanswer      
    return render_to_response('questionanswer.html',{'context':context,},context_instance=RequestContext(request))




