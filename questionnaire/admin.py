'''
Created on Jul 11, 2012

@author: mzd2
'''
from django.contrib import admin
from models import Question, QuestionGroup, Questionnaire, QuestionGroup_order, Question_order, AnswerSet, QuestionAnswer
 
class QuestionAdmin(admin.ModelAdmin):
    list_display=('label','field_type')
    



class QuestionnaireInline(admin.TabularInline):
    model = Questionnaire.questiongroup.through
    
class QuestionnaireAdmin(admin.ModelAdmin):
    inlines = [
               QuestionnaireInline,
               ]
    exclude = ('questiongroup',)
    
class QuestionGroup_OrderAdmin(admin.ModelAdmin):
    list_display = ('questiongroup','questionnaire','order_info')
    


class QuestionGroupInline(admin.TabularInline):
    model = QuestionGroup.questions.through
    
class QuestiongroupAdmin(admin.ModelAdmin):
    inlines = [
               QuestionGroupInline,
               ]   
    exclude = ('questions',)

class Question_OrderAdmin(admin.ModelAdmin):
    list_display = ('questiongroup','question','order_info')
    





class AnswerSetAdmin(admin.ModelAdmin):
    list_display=('user','questionnaire')
    
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display =('question', 'answer', 'answer_set')
    
    

    
    

admin.site.register(Question,QuestionAdmin)
admin.site.register(QuestionGroup,QuestiongroupAdmin)
admin.site.register(Questionnaire,QuestionnaireAdmin)
admin.site.register(QuestionGroup_order,QuestionGroup_OrderAdmin)
admin.site.register(Question_order,Question_OrderAdmin)
admin.site.register(AnswerSet,AnswerSetAdmin)
admin.site.register(QuestionAnswer,QuestionAnswerAdmin)