'''
Created on Jun 26, 2012

@author: ayoola_al

'''
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from models import QuestionGroup_order, Questionnaire,QuestionGroup,AnswerSet,QuestionAnswer,Question
from django.template import  RequestContext
from django.shortcuts import render_to_response
from questionnaire.forms import make_question_group_form,create_question_answer_edit_form
from django.shortcuts import get_object_or_404
from django.db.models import Q
from operator import itemgetter
from itertools import groupby
from django.db.models import Max
from django.contrib.auth.models import User
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
    
    questiongroup_id = orderedgroups[order_info-1].questiongroup.id
    this_questiongroup=get_object_or_404(QuestionGroup,pk=questiongroup_id)   
    questiongroup = this_questiongroup
    questionForm = make_question_group_form(questiongroup,questionnaire_id)

    
    
    if request.method =='POST':
        
        form=questionForm(request.POST)
        if form.is_valid():
            
            this_answer_set, created = AnswerSet.objects.get_or_create(user=request.user,questionnaire=this_questionnaire,questiongroup=this_questiongroup)
    
   
            for question, answer in form.cleaned_data.items():
                if isinstance(answer,list):
                        answer = ', '.join(answer)
                
                this_question_answer, create = QuestionAnswer.objects.get_or_create(question= get_object_or_404(Question, pk=question),answer=str(answer),answer_set=this_answer_set)
                
            if order_info >= orderedgroups.count():
                return HttpResponseRedirect(reverse('questionnaire_finish'))
            
            else: 
                order_info = order_info + 1
                return HttpResponseRedirect(reverse('handle_next_questiongroup_form', kwargs = {'questionnaire_id': questionnaire_id, 'order_info' : order_info}))
        
        else:
            
            return render_to_response('questionform.html', 
        {'form': form,'questionnaire':this_questionnaire,'questiongroup':questiongroup,},context_instance=RequestContext(request))       
            
    else:
        return render_to_response('questionform.html', 
        {'form': questionForm,'questionnaire':this_questionnaire,'questiongroup':questiongroup,},context_instance=RequestContext(request))
    
        


def finish(request):
    return render_to_response('finish.html')     
      


@login_required
def display_question_answer(request,questionnaire_id,questiongroup_id):
    '''
    display a user's most recent  question and answers for given  questiongroups in a given questionnaire
    request user is user that has answered the given questionnnaire questiongroup
    '''
    questiongroup_id=int(questiongroup_id)
    

    if request.method=='GET':
        user=request.user
        this_questionnaire=get_object_or_404(Questionnaire,pk=questionnaire_id)
        this_questiongroup=get_object_or_404(QuestionGroup,pk=questiongroup_id)
        
        q_list=QuestionAnswer.objects.values('question','answer_set').annotate(Max('id'))
        answer_max_id_list=q_list.values_list('id__max',flat=True)
       
        
        orderedgroups = QuestionGroup_order.objects.filter(questionnaire= this_questionnaire).order_by('order_info')    
        groups_list=[(x.questiongroup) for x in orderedgroups]
        
        y=QuestionAnswer.objects.filter(Q(answer_set__user_id=user,answer_set__questiongroup=this_questiongroup,answer_set__questionnaire=this_questionnaire)).filter(id__in=answer_max_id_list)          
        questionanswer=[(x.question.id,x.question.label ,x.answer) for x in y]
        

        context=questionanswer
        return render_to_response('display_questionanswer.html',{'context':context,'user':user,'questionnaire':this_questionnaire,'questiongroup_id':questiongroup_id,'groups_list':groups_list,},context_instance=RequestContext(request))




@login_required
def edit_question_answer(request,questionnaire_id,questiongroup_id):
    '''
    edit a user most recent answers for a given questiongroup in a given questionnaire 
    pre-populates form with most recent answers 
    does not overwrite questionanswer it create new questionanswer  for answerset   for purpose of keeping queationanswers trail
     
    '''
    
    user=request.user   
    questionnaire_id=int(questionnaire_id)
    questiongroup_id=int(questiongroup_id)
    this_questionnaire=get_object_or_404(Questionnaire,pk=questionnaire_id)
    this_questiongroup=get_object_or_404(QuestionGroup,pk=questiongroup_id)
        
    orderedgroups = QuestionGroup_order.objects.filter(questionnaire= this_questionnaire).order_by('order_info')    
    groups_list=[(x.questiongroup.id) for x in orderedgroups]

    editForm= create_question_answer_edit_form(user,this_questionnaire,this_questiongroup) 
             
    if  request.method == "POST":
        
        form=editForm(request.POST)
        
        if form.is_valid():
                        
            this_answer_set, created = AnswerSet.objects.get_or_create(user=request.user,questionnaire=this_questionnaire,questiongroup=this_questiongroup)
            
            
            for question, answer in form.cleaned_data.items():
                if isinstance(answer,list):
                        answer = ', '.join(answer)
                        

                this_question_answer= QuestionAnswer(question= get_object_or_404(Question, pk=question),answer=answer,answer_set=this_answer_set)
                this_question_answer.save()
                
                                                  
            return HttpResponseRedirect(reverse('questionnaire_finish'))            
        else:
                       
       
            return render_to_response('edit_questionanswer_form.html', 
        {'form': form,'user':user,'questionnaire':this_questionnaire,'questiongroup_id':questiongroup_id,'groups_list':groups_list,},context_instance=RequestContext(request))
    
    else :
        return render_to_response('edit_questionanswer_form.html', 
                                      {'form': editForm,'user':user,'questionnaire':this_questionnaire,'questiongroup_id':questiongroup_id,'groups_list':groups_list,},context_instance=RequestContext(request))



@login_required    
def all_question_answers_for_questiongroup(request,user_id,questionnaire_id,questiongroup_id):
    
    '''
    show trail all questions and  answers for  given questiongroup in a questionnaire for a given user_id 
    user_id is not request.user ,instead user_id is auth user
    permission  still need to be set and implemented as required
   
    '''
    questiongroup_id=int(questiongroup_id)   
    
    if request.method=='GET':
        user =get_object_or_404(User,pk=user_id)
        this_questionnaire=get_object_or_404(Questionnaire,pk=questionnaire_id)
        this_questiongroup=get_object_or_404(QuestionGroup,pk=questiongroup_id)
        
        orderedgroups = QuestionGroup_order.objects.filter(questionnaire= this_questionnaire).order_by('order_info')    
        groups_list=[(x.questiongroup) for x in orderedgroups]
        
        y=QuestionAnswer.objects.filter(Q(answer_set__user_id=user,answer_set__questiongroup=this_questiongroup,answer_set__questionnaire=this_questionnaire))
           
        questionanswer=[(x.question.id,x.question.label ,x.answer) for x in y]
       
       
        qs= sorted(set(questionanswer),key=itemgetter(0))            
        questionanswer_list = list(map(itemgetter(0), groupby(qs)))        
        context= questionanswer_list

        return render_to_response('all_questionanswers.html',{'context':context,'user':user,'questionnaire':this_questionnaire,'questiongroup_id':questiongroup_id,'groups_list':groups_list,},context_instance=RequestContext(request))



@login_required
def questionnaire_detail_list(request,questionnaire_id):
    '''
    show  detail list as links  for all questiongroups in a given questionnaire ordered by order_info
    links can be use to edit or display given  questionanswer for questiongroups in questionnaire
    '''
    if request.method=='GET':
        
        this_questionnaire=get_object_or_404(Questionnaire,pk=questionnaire_id)
        orderedgroups = QuestionGroup_order.objects.filter(questionnaire= this_questionnaire).order_by('order_info')    
        groups_list=[(x.questiongroup) for x in orderedgroups]
        context = groups_list
        return render_to_response('questionnaire_detail.html',{'context':context, 'questionnaire':this_questionnaire,},context_instance=RequestContext(request))

    
    
    
    
