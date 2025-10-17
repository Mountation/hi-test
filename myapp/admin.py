# myapp/admin.py
from django.contrib import admin
from .models import EvaluationSet, Corpus, EvaluationRun, CorpusResult
# Register your models here.


@admin.register(EvaluationSet)
class EvaluationSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Corpus)
class CorpusAdmin(admin.ModelAdmin):
    list_display = ('evaluation_set', 'intent', 'created_at')
    list_filter = ('intent', 'created_at', 'evaluation_set')
    search_fields = ('content', 'expected_response')

@admin.register(EvaluationRun)
class EvaluationRunAdmin(admin.ModelAdmin):
    list_display = ('evaluation_set', 'run_name', 'status', 'start_time', 'end_time', 'version')
    list_filter = ('status', 'start_time', 'evaluation_set')
    search_fields = ('run_name',)

@admin.register(CorpusResult)
class CorpusResultAdmin(admin.ModelAdmin):
    list_display = ('evaluation_run', 'corpus', 'status', 'score', 'version')
    list_filter = ('status', 'evaluation_run', 'score')