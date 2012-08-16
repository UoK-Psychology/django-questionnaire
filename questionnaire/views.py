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



def questionnaire_index (request):
    questionnaire = Questionnaire.objects.all()
    answer_set = AnswerSet.objects.all()
    
    group_list=[x for x in questionnaire]
    
    return render_to_response('questionnaire_index.html',{'group_list': group_list},context_instance=RequestContext(request))
    

@login_required
def handle_next_questiongroup_form(request,questionnaire_id,order_info=None):
    
    '''
        TODO: Document me!! in particular what are questionniare_id and order_id and how are they used
    '''
    questionnaire_id = int(questionnaire_id)
    
    if order_info==None:
        order_info = 1 

    else:
        order_info = int(order_info)
        
    this_questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_id)
    

    
    #Start refactor target:
    #TODO:This is a bit over complicated, you are juggling a lot variables around when your aim is simply to get a reference to the questiongroup, and create a form based on it
    #This could even be refactored out into a module function which could then be seperately unit tested
    orderedgroups = this_questionnaire.get_ordered_groups()
    questiongroup_id = orderedgroups[order_info-1].questiongroup.id
    this_questiongroup=get_object_or_404(QuestionGroup,pk=questiongroup_id)  #TODO: you have already got a reference to the questiongroup object, no need to use the id to get it again!
    questiongroup = this_questiongroup # TODO: Why not just use questiongroup as the variable name from the start?
    questionForm = make_question_group_form(questiongroup,questionnaire_id)
    #End Refactor target
    
    
    if request.method =='POST':
        
        form=questionForm(request.POST)
        if form.is_valid():
            
            this_answer_set, created = AnswerSet.objects.get_or_create(user=request.user,questionnaire=this_questionnaire,questiongroup=this_questiongroup)
    
   
            for question, answer in form.cleaned_data.items():
                if isinstance(answer,list):
                        answer = ', '.join(answer)
                
                # TODO: I wonder if there is a more efficient way of doing this
                #my understanding is that we are trying to cope with a situtation where we could either be dealing
                #with a field that is new (never been submitted before) or existing but has been edited, or existing and has not changed
                #This method works because it asks the database for each field if an QuestionAnswer exists with this signature
                #and if not it creates it, but this is inefficient as it will lead to lots of calls to the database
                #you could use the changed_data property on the form to achieve the same thing without going to the database?
                this_question_answer, create = QuestionAnswer.objects.get_or_create(question= get_object_or_404(Question, pk=question),answer=str(answer),answer_set=this_answer_set)
                
            if order_info >= orderedgroups.count():#this is the last group in the questionnaire
                return HttpResponseRedirect(reverse('questionnaire_finish'))
            
            else: 
                order_info = order_info + 1
                return HttpResponseRedirect(reverse('handle_next_questiongroup_form', kwargs = {'questionnaire_id': questionnaire_id, 'order_info' : order_info}))
        
        else:#TODO: you don't need this else block as it repeats the code below it
            
            return render_to_response('questionform.html', 
        {'form': form,'questionnaire':this_questionnaire,'questiongroup':questiongroup,},context_instance=RequestContext(request))       
            
    else:#TODO: this code doesn't need to be in an else block , this code could be left outside the if statement, as if you have got this far then either it is a get request or an invalid post request, and both should be handled in the same way
        return render_to_response('questionform.html', 
        {'form': questionForm,'questionnaire':this_questionnaire,'questiongroup':questiongroup,},context_instance=RequestContext(request))
    
        


def finish(request):
    '''
        TODO: Document me!!
    '''
    return render_to_response('finish.html')     #you will still want to pass this through the RequestContext, which enables middleware to add things to the response  eg. context_instance=RequestContext(request)
      


@login_required
def display_question_answer(request,questionnaire_id,questiongroup_id):
    '''
    display a user's most recent  question and answers for given  questiongroups in a given questionnaire
    request user is user that has answered the given questionnnaire questiongroup
    '''
    questiongroup_id=int(questiongroup_id)

    # TODO: is it really nescessary to check that it is a GET request, worst comes to worse if someone posts to this you will just treat it like a GET? Additionaly if you don't return anything from this function then an error will be raised so if it is important that it be a get request there should be an else that either raises an appropriate message (404?!), or renders a hepful erorr message page
    user=request.user
    this_questionnaire=get_object_or_404(Questionnaire,pk=questionnaire_id)
    this_questiongroup=get_object_or_404(QuestionGroup,pk=questiongroup_id)
        
        #TODO can you explain this?
## EXPLAINATION  given that max id of an object  represent  most recent created object otherwise you have to get created date timestamp .Max is django built in fuction. this retrieve max ids for Questionanswer object  based on question and answer_set ,annotate constraint the objects to the only objects with maximum id
## second line flatten the queryset to list of only max-ids of the most recent  questionanswer .
    q_list=QuestionAnswer.objects.values('question','answer_set').annotate(Max('id'))  
    answer_max_id_list=q_list.values_list('id__max',flat=True)
       
        
    #TODO: Why do you need to get the ordered list of groups? you have specified a specific question group_id as an argument for the function?
#   orderedgroups = QuestionGroup_order.objects.filter(questionnaire= this_questionnaire).order_by('order_info')#TODO: use .get_ordered_groups() for this as it abstracts the need to know about the ordering implementation and you won't need the next line as it returns a list of questiongroups
    orderedgroups=this_questionnaire.get_ordered_groups()
    
##EXPLAINATION  group list is passed to the template to display links to  other question groups in the  given questionnaire so it make easier for user to navigate to other questionanswer display in the questionnaire
    groups_list=[(x.questiongroup) for x in orderedgroups]
        
    #TODO: this seems a quite complex, and is difficult to follow, either add a comment to explain what you are doing, or consider refactoring to make it simpler?
   ##EXPLAINATION  using django Complex lookups with Q objects use for join query , it retrieve all the questionanswer related objects where the user is this user for this question group and this questionnaire
   ##  it does this by span relationship i.e double underscore  between QuestionAnswer  answerset attribute  and Answerset object attributes i.e user ,questiongroup,questionnaire this referential relationship is already defined in the models
   ##   since we are only interested in the most recent questionanswer filter(id__in=answer_max_id_list) further filter all related questionanswer objects to the one qa objects in the max id list .
   ##   [(x.question.id,x.question.label ,x.answer)for x in y] .  this retrieve the question label and the answer for  each questionanswer in the most recent questionanswer put them in a list.
    y=QuestionAnswer.objects.filter(Q(answer_set__user_id=user,answer_set__questiongroup=this_questiongroup,answer_set__questionnaire=this_questionnaire)).filter(id__in=answer_max_id_list)          
    
    questionanswer=[(x.question.id,x.question.label ,x.answer) for x in y]

    #TODO: Be careful using the variable context, it has special significance, and using this way would be confusing to the reader of your code
        #TODO: you don't need to explicitly put user into your responses context, it will get put there by virtue of using context_instance=RequestContext(request)
    ## EXPLAINATION : context variable REMOVED
    return render_to_response('display_questionanswer.html',{'questionanswer':questionanswer,'questionnaire':this_questionnaire,'questiongroup_id':questiongroup_id,'groups_list':groups_list,},context_instance=RequestContext(request))




@login_required
def edit_question_answer(request,questionnaire_id,questiongroup_id):
    '''
    edit a user most recent answers for a given questiongroup in a given questionnaire 
    pre-populates form with most recent answers 
    does not overwrite questionanswer it create new questionanswer  for answerset   for purpose of keeping queationanswers trail
     
    '''
    
    user=request.user   
#    questionnaire_id=int(questionnaire_id)#TODO: Do you really need to cast to an int?
    questiongroup_id=int(questiongroup_id)#TODO: Do you really need to cast to an int?
    this_questionnaire=get_object_or_404(Questionnaire,pk=questionnaire_id)
    this_questiongroup=get_object_or_404(QuestionGroup,pk=questiongroup_id)
        
    #TODO: use .get_ordered_groups() for this as it abstracts the need to know about the ordering implementation and you won't need the next line as it returns a list of questiongroups
#    orderedgroups = QuestionGroup_order.objects.filter(questionnaire= this_questionnaire).order_by('order_info')
    orderedgroups=this_questionnaire.get_ordered_groups() 
    groups_list=[(x.questiongroup.id) for x in orderedgroups]

    editForm= create_question_answer_edit_form(user,this_questionnaire,this_questiongroup) 
             
    if  request.method == "POST":
        
        form=editForm(request.POST)
        
        if form.is_valid():
            
            #TODO this logic seems very similar to the handle_next_questiongroup_form function consider refactoring, perhaps abstracting this logic to another function that can be used by both views?        
            this_answer_set, created = AnswerSet.objects.get_or_create(user=request.user,questionnaire=this_questionnaire,questiongroup=this_questiongroup)
            
            
            for question, answer in form.cleaned_data.items():
                if isinstance(answer,list):
                        answer = ', '.join(answer)
                        

                this_question_answer= QuestionAnswer(question= get_object_or_404(Question, pk=question),answer=answer,answer_set=this_answer_set)
                this_question_answer.save()
                
                                                  
            return HttpResponseRedirect(reverse('questionnaire_finish'))            
        else:
                       
#Start refactor target:  
#TODO: you should be able to refactor this so that you dont duplicate all of this code, if you get rid of the else clauses, if you get this far then you are either
#dealing with an invalid form or a get request, and you should be able to hand them in the same way
            return render_to_response('edit_questionanswer_form.html', 
       {'form': form,'questionnaire':this_questionnaire,'questiongroup_id':questiongroup_id,'groups_list':groups_list,},context_instance=RequestContext(request))
    #TODO: you don't need to explicitly put user into your responses context, it will get put there by virtue of using context_instance=RequestContext(request)
    else :
        return render_to_response('edit_questionanswer_form.html', 
                                      {'form': editForm,'questionnaire':this_questionnaire,'questiongroup_id':questiongroup_id,'groups_list':groups_list,},context_instance=RequestContext(request))

#End refactor target

@login_required     
def all_question_answers_for_questiongroup(request,user_id,questionnaire_id,questiongroup_id):
    
    '''
    show trail all questions and  answers for  given questiongroup in a questionnaire for a given user_id 
    user_id is not request.user ,instead user_id is auth user
    permission  still need to be set and implemented as required
   
    '''
    questiongroup_id=int(questiongroup_id)   #TODO is this really nescessary?
    
    #TODO: is this really nescessay?
        
        #TODO: This logic seems to be very similar to display_question_answer consider refactoring and abstracting the common logic into a shared function
    user =get_object_or_404(User,pk=user_id)
    this_questionnaire=get_object_or_404(Questionnaire,pk=questionnaire_id)
    this_questiongroup=get_object_or_404(QuestionGroup,pk=questiongroup_id)
        
        #TODO: use .get_ordered_groups() for this as it abstracts the need to know about the ordering implementation and you won't need the next line as it returns a list of questiongroups
#        orderedgroups = QuestionGroup_order.objects.filter(questionnaire= this_questionnaire).order_by('order_info') 
    orderedgroups=this_questionnaire.get_ordered_groups()   
    groups_list=[(x.questiongroup) for x in orderedgroups]
        
        #TODO explain what this does
    y=QuestionAnswer.objects.filter(Q(answer_set__user_id=user,answer_set__questiongroup=this_questiongroup,answer_set__questionnaire=this_questionnaire)) 
    questionanswer=[(x.question.id,x.question.label ,x.answer) for x in y]
       
       
    qs= sorted(set(questionanswer),key=itemgetter(0))            
    questionanswer_list = list(map(itemgetter(0), groupby(qs)))        
#        context= questionanswer_list

        #
    return render_to_response('all_questionanswers.html',{'questionanswer_list':questionanswer_list,'user':user,'questionnaire':this_questionnaire,'questiongroup_id':questiongroup_id,'groups_list':groups_list,},context_instance=RequestContext(request))



@login_required
def questionnaire_detail_list(request,questionnaire_id):
    '''
    show  detail list as links  for all questiongroups in a given questionnaire ordered by order_info
    links can be use to edit or display given  questionanswer for questiongroups in questionnaire
    '''
   
        
    this_questionnaire=get_object_or_404(Questionnaire,pk=questionnaire_id)
        
    #TODO: use .get_ordered_groups() for this as it abstracts the need to know about the ordering implementation and you won't need the next line as it returns a list of questiongroups
#        orderedgroups = QuestionGroup_order.objects.filter(questionnaire= this_questionnaire).order_by('order_info') 
    groups_list=this_questionnaire.get_ordered_groups()    
#    groups_list=[(x.questiongroup) for x in orderedgroups]
   
        
        #TODO: careful about using context as a variable now it has special significance in views
   
        #TODO: you don't need to explicitly put user into your responses context, it will get put there by virtue of using context_instance=RequestContext(request)
    return render_to_response('questionnaire_detail.html',{'groups_list': groups_list, 'questionnaire':this_questionnaire,},context_instance=RequestContext(request))

    
    
    
    
