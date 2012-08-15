'''
Created on Jul 11, 2012

@author: mzd2
'''
from django.contrib import admin
from models import Question, QuestionGroup, Questionnaire, QuestionGroup_order, Question_order, AnswerSet, QuestionAnswer,QuestionAdminForm
 
class QuestionAdmin(admin.ModelAdmin):
    '''
    custom form for display and creating question in the admin 
    
    '''
    form=QuestionAdminForm
    list_display=('label','field_type','selectoptions_list')
    def selectoptions_list(self, obj):
        '''
        @return: selectoptions List  as string separated comma e.g A,B,C if question has selectoption
        otherwise return  None
        '''
        if obj.selectoptions:
            return ', '.join(str(x) for x in obj.selectoptions)
        return None


class QuestionnaireInline(admin.TabularInline):
    '''
        TODO: Document me!!
    '''
    model = Questionnaire.questiongroup.through
    
class QuestionnaireAdmin(admin.ModelAdmin):
    '''
        TODO: Document me!!
    '''
    inlines = [
               QuestionnaireInline,
               ]
    exclude = ('questiongroup',)
    
class QuestionGroup_OrderAdmin(admin.ModelAdmin):
    '''
        TODO: Document me!!
    '''
    list_display = ('questiongroup','questionnaire','order_info')
    


class QuestionGroupInline(admin.TabularInline):
    '''
        TODO: Document me!!
    '''
    model = QuestionGroup.questions.through
    
class QuestiongroupAdmin(admin.ModelAdmin):
    '''
        TODO: Document me!!
    '''
    inlines = [
               QuestionGroupInline,
               ]   
    exclude = ('questions',)

class Question_OrderAdmin(admin.ModelAdmin):
    '''
        TODO: Document me!!
    '''
    list_display = ('questiongroup','question','order_info')
    





class AnswerSetAdmin(admin.ModelAdmin):
    '''
        TODO: Document me!!
    '''
    list_display=('user','questionnaire','questiongroup')
    
class QuestionAnswerAdmin(admin.ModelAdmin):
    '''
        TODO: Document me!!
    '''
    list_display =('question', 'answer', 'answer_set')
    
    

    
    

admin.site.register(Question,QuestionAdmin)
admin.site.register(QuestionGroup,QuestiongroupAdmin)
admin.site.register(Questionnaire,QuestionnaireAdmin)
admin.site.register(QuestionGroup_order,QuestionGroup_OrderAdmin)
admin.site.register(Question_order,Question_OrderAdmin)
admin.site.register(AnswerSet,AnswerSetAdmin)
admin.site.register(QuestionAnswer,QuestionAnswerAdmin)