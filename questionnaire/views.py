from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from models import QuestionGroup_order, Questionnaire
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

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
    print orderedgroups[order_info-1].questiongroup.id    
    
    
    
    
        
    if order_info == orderedgroups.count():
            this = 'this is the last one!'
            print this
            
    else:
            this = 'Continue! pass order_info+1 !'
            print this
        
    

    
     
    
    
