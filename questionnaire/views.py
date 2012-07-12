from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from models import QuestionGroup_order, Questionnaire
from django.template import  RequestContext
from django.shortcuts import render_to_response
from questionnaire.forms import make_question_group_form

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
    
    questionForm = make_question_group_form(questiongroup_id)
    
    
    
    
    if request.method =='POST':
    
        
        if order_info == orderedgroups.count():
            this = 'this is the last one!'
            print this
            return HttpResponseRedirect(reverse('finish'))
            
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
     

    
