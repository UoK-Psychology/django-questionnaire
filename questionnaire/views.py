from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from models import Questionnaire,QuestionGroup,AnswerSet,QuestionAnswer,Question
from django.template import  RequestContext
from django.shortcuts import render_to_response
from questionnaire.forms import QuestionGroupForm
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db.models import Max
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


@login_required
def questionnaire_index (request, template_name):
    questionnaire = Questionnaire.objects.all()
    group_list=[x for x in questionnaire]
    
    return render_to_response(template_name,{'group_list': group_list},context_instance=RequestContext(request))
    



@login_required
def do_questionnaire(request,questionnaire_id,template_name,next_form_name, finished_url,order_index=None):
    
    '''
        This view handles the presentation and submission of questiongroups. You must always specify a 
        questionnaire, and optionally you make specify an order index. The order index represents a question group in
        the sequence of ordered groups for the given questionnaire. The index is zero based and is not related
        to the question group's id. If the index doesn't exist a 404 error will be thrown.
        If the user has already asnwered the question group for this questionnaire, then this view will allow them to 
        display, and allow them to edit their previous answers.
    '''
    questionnaire_id = int(questionnaire_id)
    
    if order_index==None:
        order_index = 0# zero based index 
    else:
        order_index = int(order_index)
        
    this_questionnaire = get_object_or_404(Questionnaire, pk=questionnaire_id)
    
    try:#get the question group based on the questionnaire and the index in the ordered list of groups 
        questiongroup , count = this_questionnaire.get_group_for_index(order_index)
    except IndexError:#if it doesn't exist we should throw a 404 not an INdexError
        raise Http404
    
    this_answer_set = AnswerSet.objects.get_or_create(user=request.user,
                                                                       questionnaire=this_questionnaire,
                                                                       questiongroup=questiongroup)[0]#we don't care if it had been created so we only need to first index of the tuple
    
    form=QuestionGroupForm(questiongroup=questiongroup,initial=this_answer_set, data=request.POST or None)
    
    if request.method =='POST':
        if form.is_valid():
            
            for question, answer in form.cleaned_data.items():
                if isinstance(answer,list):
                        answer = ', '.join(answer)
                
                if question in form.changed_data:
                    QuestionAnswer.objects.create(question= get_object_or_404(Question, pk=question),
                                                answer=str(answer),
                                                answer_set=this_answer_set)
                        
                
                
            if count == 0:#this is the last group in the questionnaire
                return HttpResponseRedirect(finished_url)
            
            else: 
                order_info = order_index + 1
                return HttpResponseRedirect(reverse(next_form_name, kwargs = {'questionnaire_id': questionnaire_id, 'order_index' : order_info}))
            
    return render_to_response(template_name, 
    {'form': form ,'questionnaire':this_questionnaire,'questiongroup':questiongroup,},context_instance=RequestContext(request))
    
def finish(request, template_name):
    '''
        TODO: Document me!!
    '''
    return render_to_response(template_name,context_instance=RequestContext(request))
      


@login_required
def display_question_answer(request,questionnaire_id,questiongroup_id,template_name):
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
    return render_to_response(template_name,{'questionanswer':questionanswer,'questionnaire':this_questionnaire,'questiongroup_id':questiongroup_id,'groups_list':groups_list,},context_instance=RequestContext(request))






@login_required     
def all_question_answers_for_questiongroup(request,user_id,questionnaire_id,questiongroup_id, template_name):
    
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
    this_answer_set = get_object_or_404(AnswerSet, user=user, questionnaire=this_questionnaire, questiongroup=this_questiongroup)
        
        #TODO: use .get_ordered_groups() for this as it abstracts the need to know about the ordering implementation and you won't need the next line as it returns a list of questiongroups
#        orderedgroups = QuestionGroup_order.objects.filter(questionnaire= this_questionnaire).order_by('order_info') 
    orderedgroups=this_questionnaire.get_ordered_groups()   
    groups_list=[(x.questiongroup) for x in orderedgroups]
        
        #TODO explain what this does
       
          
    questionanswer_list = this_answer_set.get_latest_question_answers()     
#        context= questionanswer_list

        #
    return render_to_response(template_name,{'questionanswer_list':questionanswer_list,'user':user,'questionnaire':this_questionnaire,'questiongroup_id':questiongroup_id,'groups_list':groups_list,},context_instance=RequestContext(request))



@login_required
def questionnaire_detail_list(request,questionnaire_id, template_name):
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
    return render_to_response(template_name,{'groups_list': groups_list, 'questionnaire':this_questionnaire,},context_instance=RequestContext(request))

    
    
    
    
