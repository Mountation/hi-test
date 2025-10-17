# myapp/views/dataset.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from ..models import EvaluationSet, Corpus
from ..utils import parse_excel_file, bulk_create_corpora
import time
from collections import Counter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging

# Logger for this module
logger = logging.getLogger(__name__)

def list_datasets(request):
    """
    列出所有评测集
    """
    evaluation_sets = EvaluationSet.objects.filter(status='active')
    return render(request, 'dataset/list.html', {'evaluation_sets': evaluation_sets})

def create_dataset(request):
    """
    创建评测集：上传Excel文件并将其内容存储到数据库
    """
    # 处理GET请求，显示创建页面
    if request.method != 'POST':
        return render(request, 'dataset/create.html')
    
    # 处理POST请求
    if not request.FILES.get('excel_file'):
        return JsonResponse({
            'status': 'error',
            'message': '请选择要上传的Excel文件'
        })
    
    excel_file = request.FILES['excel_file']
    evaluation_set_name = request.POST.get('evaluation_set_name', '').strip()
    evaluation_set_desc = request.POST.get('evaluation_set_desc', 'Uploaded from Excel file')
    
    # 检查评测集名称
    if not evaluation_set_name:
        return JsonResponse({
            'status': 'error',
            'message': '请输入评测集名称'
        })
    
    # 检查评测集名称是否已存在
    if EvaluationSet.objects.filter(name=evaluation_set_name).exists():
        return JsonResponse({
            'status': 'error',
            'message': f'评测集名称 "{evaluation_set_name}" 已存在，请使用其他名称'
        })
    
    logger.info('create_dataset called by %s', request.META.get('REMOTE_ADDR'))
    try:
        # 解析 Excel 文件（返回 header 与行生成器）
        headers, rows_gen = parse_excel_file(excel_file)

        # 创建评测集
        evaluation_set = EvaluationSet.objects.create(
            name=evaluation_set_name,
            description=evaluation_set_desc,
            status='active'
        )

        # 使用工具函数做批量插入并收集统计
        stats = bulk_create_corpora(evaluation_set, rows_gen, batch_size=1000, logger_obj=logger)

        return JsonResponse({
            'status': 'success',
            'message': f'成功创建评测集 "{evaluation_set_name}"，导入了 {stats["success_count"]} 条语料记录'
        })
    except Exception as e:
        logger.exception('Failed to create EvaluationSet "%s": %s', evaluation_set_name if 'evaluation_set_name' in locals() else '<unknown>', e)
        return JsonResponse({
            'status': 'error',
            'message': f'上传文件失败: {str(e)}'
        })

def delete_dataset(request, dataset_id):
    """
    删除评测集及其关联的所有语料
    """
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': '无效的请求方法'
        })
    
    # 获取评测集对象
    evaluation_set = get_object_or_404(EvaluationSet, id=dataset_id)

    logger.info('delete_dataset called for id=%s by %s', dataset_id, request.META.get('REMOTE_ADDR'))
    try:
        # 获取关联的语料数量，用户返回信息（在删除前统计）
        corpus_qs = Corpus.objects.filter(evaluation_set=evaluation_set)
        corpus_count = corpus_qs.count()

        evaluation_set_name = evaluation_set.name

        # 使用事务执行批量删除：先以 QuerySet 方式删除所有语料（在 DB 层一次性删除，避免逐条触发 ORM delete）
        # 然后删除评测集本身
        with transaction.atomic():
            if corpus_count > 0:
                deleted_info = corpus_qs.delete()
                logger.info('Deleted corpora for EvaluationSet id=%s: %s', evaluation_set.id, deleted_info)

            # 删除评测集（单条删除，开销很小）
            EvaluationSet.objects.filter(id=evaluation_set.id).delete()
            logger.info('Deleted EvaluationSet id=%s name="%s"', evaluation_set.id, evaluation_set_name)

        return JsonResponse({
            'status': 'success',
            'message': f'成功删除评测集 "{evaluation_set_name}"，删除了 {corpus_count} 条语料记录'
        })
    except Exception as e:
        logger.exception('Failed to delete EvaluationSet id=%s: %s', dataset_id, e)
        return JsonResponse({
            'status': 'error',
            'message': f'删除评测集失败: {str(e)}'
        })
    
def view_dataset(request, dataset_id):
    """
    查看评测集详情，包括其中的所有语料
    """
    # 获取评测集对象
    evaluation_set = get_object_or_404(EvaluationSet, id=dataset_id)
    
    # 获取该评测集下的所有语料（作为 QuerySet）
    corpora_qs = Corpus.objects.filter(evaluation_set=evaluation_set).order_by('created_at')

    # 分页：每页显示 10 条
    page = request.GET.get('page', 1)
    paginator = Paginator(corpora_qs, 10)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    corpora_count = corpora_qs.count()
    logger.debug('view_dataset id=%s page=%s total_corpora=%d', dataset_id, page, corpora_count)

    context = {
        'evaluation_set': evaluation_set,
        # 将 page_obj 传入模板以便渲染分页控件，corpora 在模板中仍可用于迭代
        'corpora': page_obj,
        'page_obj': page_obj,
        'corpora_count': corpora_count,
        'start_index': page_obj.start_index(),
        'end_index': page_obj.end_index(),
    }
    
    return render(request, 'dataset/view.html', context)

def run_dataset_page(request):
    """
    运行评测集页面
    """
    # 获取所有活跃的评测集
    evaluation_sets = EvaluationSet.objects.filter(status='active')
    
    # 为每个评测集预处理意图数据
    for eval_set in evaluation_sets:
        # 获取该评测集下的所有非空意图
        intents = Corpus.objects.filter(
            evaluation_set=eval_set
        ).exclude(
            intent__isnull=True
        ).exclude(
            intent__exact=''
        ).values_list('intent', flat=True)
        
        # 统计意图出现次数并获取前5个最常见的意图
        intent_counter = Counter(intents)
        eval_set.top_intents = [intent for intent, count in intent_counter.most_common(5)]
        eval_set.intent_count = len(intent_counter)
    
    return render(request, 'dataset/run.html', {'evaluation_sets': evaluation_sets})