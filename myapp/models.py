# myapp/models.py
from django.db import models
import json
# Create your models here.
class EvaluationSet(models.Model):
    STATUS_CHOICES = [
        ('active','Active'),
        ('inactive','Inactive'),
    ]
    name = models.CharField(max_length=255, unique=True, verbose_name="评测集名称")
    description = models.TextField(blank=True, null=True, verbose_name="评测集描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="状态")
    
    class Meta:
        db_table = 'evaluation_sets'
        verbose_name = "评测集"
        verbose_name_plural = "评测集"
        
    def __str__(self):
        return self.name
    
    def get_corpora_count(self):
        return self.corpus_set.count()

class Corpus(models.Model):
    evaluation_set = models.ForeignKey(EvaluationSet, on_delete=models.CASCADE, verbose_name="所属评测集")
    content = models.TextField(verbose_name="语料内容")
    expected_response = models.TextField(blank=True, null=True, verbose_name="预期结果")
    intent = models.CharField(max_length=100, blank=True, null=True, verbose_name="意图")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = 'corpus'
        verbose_name = "语料"
        verbose_name_plural = "语料"
        indexes = [
            models.Index(fields=['evaluation_set', 'intent'], name='idx_set_intent'),
        ]
        
    def __str__(self):
        return f"{self.evaluation_set.name} - {self.intent or '未指定意图'}"

class EvaluationRun(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('running', 'Running'),
    ]
    
    evaluation_set = models.ForeignKey(EvaluationSet, on_delete=models.CASCADE, verbose_name="关联评测集")
    run_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="本次执行名称")
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="开始时间")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="结束时间")
    duration = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True, verbose_name="总耗时(秒)")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, blank=True, null=True, verbose_name="执行状态")
    config = models.JSONField(blank=True, null=True, verbose_name="配置参数")
    summary_metrics = models.JSONField(blank=True, null=True, verbose_name="整体指标汇总")
    version = models.CharField(max_length=50, blank=True, null=True, verbose_name="版本", default='1.0.0')
    
    class Meta:
        db_table = 'evaluation_runs'
        verbose_name = "评测执行记录"
        verbose_name_plural = "评测执行记录"
        indexes = [
            models.Index(fields=['start_time'], name='idx_run_time'),
        ]
        
    def __str__(self):
        return f"{self.evaluation_set.name} - {self.run_name or self.start_time}"

class CorpusResult(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    evaluation_run = models.ForeignKey(EvaluationRun, on_delete=models.CASCADE, verbose_name="关联的评测执行记录")
    corpus = models.ForeignKey(Corpus, on_delete=models.CASCADE, verbose_name="关联的语料")
    actual_response = models.TextField(verbose_name="实际结果", default="")
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="评分")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, blank=True, null=True, verbose_name="单条语料执行状态")
    error_msg = models.TextField(blank=True, null=True, verbose_name="错误信息")
    version = models.CharField(max_length=50, blank=True, null=True, verbose_name="版本", default='1.0.0')
    execution_order = models.IntegerField(blank=True, null=True, verbose_name="执行顺序")
    
    class Meta:
        db_table = 'corpus_results'
        verbose_name = "语料执行结果"
        verbose_name_plural = "语料执行结果"
        constraints = [
            models.UniqueConstraint(fields=['evaluation_run', 'corpus'], name='uk_run_corpus')
        ]
        indexes = [
            models.Index(fields=['corpus'], name='idx_corpus_results'),
        ]
        
    def __str__(self):
        return f"Result for {self.corpus} in {self.evaluation_run}"