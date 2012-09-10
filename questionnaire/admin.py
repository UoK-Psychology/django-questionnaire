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
        This class acts as 'connecting' model class that connects many to many relationship
        between Questionnaire and QuestionGroup
        
    '''
    model = Questionnaire.questiongroup.through
    
class QuestionnaireAdmin(admin.ModelAdmin):
    '''
         Inlines enables the admin interface the ability the ability to edit models on the same page as a parent model.
         
    '''
    inlines = [
               QuestionnaireInline,
               ]
    exclude = ('questiongroup',)
    
class QuestionGroup_OrderAdmin(admin.ModelAdmin):
    '''
        list_display is use to control which fields are displayed on the change list page of the admin.
        i.e It also acts as a register/management of the model class, editing and addition of its object from the admin view.
    '''
    list_display = ('questiongroup','questionnaire','order_info')
    


class QuestionGroupInline(admin.TabularInline):
    '''
        This class acts as 'connecting' model class that connects many to many relationship
        between Questiongroup and Questions
        
    '''
    model = QuestionGroup.questions.through
    
class QuestiongroupAdmin(admin.ModelAdmin):
    '''
        Inlines enables the admin interface the ability the ability to edit models on the same page as a parent model.
    '''
    inlines = [
               QuestionGroupInline,
               ]   
    exclude = ('questions',)

class Question_OrderAdmin(admin.ModelAdmin):
    '''
        list_display is use to control which fields are displayed on the change list page of the admin.
    '''
    list_display = ('questiongroup','question','order_info')
    





class AnswerSetAdmin(admin.ModelAdmin):
    '''
    list_display is use to control which fields are displayed on the change list page of the admin.
    i.e It also acts as a register/management of the model class, editing and addition of its object from the admin view.
       
    '''
    list_display=('user','questionnaire','questiongroup')
    
class QuestionAnswerAdmin(admin.ModelAdmin):
    '''
    list_display is use to control which fields are displayed on the change list page of the admin.
    i.e It also acts as a register/management of the model class, editing and addition of its object from the admin view.
    '''
    list_display =('question', 'answer', 'answer_set')
    
    

    
    

admin.site.register(Question,QuestionAdmin)
admin.site.register(QuestionGroup,QuestiongroupAdmin)
admin.site.register(Questionnaire,QuestionnaireAdmin)
admin.site.register(QuestionGroup_order,QuestionGroup_OrderAdmin)
admin.site.register(Question_order,Question_OrderAdmin)
admin.site.register(AnswerSet,AnswerSetAdmin)
admin.site.register(QuestionAnswer,QuestionAnswerAdmin)