# myapp/views/home.py
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from myapp.AIClient import AIClient
from ..models import EvaluationSet, Corpus, EvaluationRun
import threading
from ..views.evaluation import process_dataset_async

def home(request):
    """
    首页视图
    """
    # 获取所有评测集及其统计信息
    evaluation_sets = EvaluationSet.objects.filter(status='active').prefetch_related('corpus_set')
    
    # 为每个评测集添加语料数量
    for eval_set in evaluation_sets:
        eval_set.corpora_count = eval_set.corpus_set.count()
        # 获取最新的评测运行记录
        eval_set.latest_run = EvaluationRun.objects.filter(evaluation_set=eval_set).order_by('-start_time').first()
    
    # 获取最近的评测运行记录
    recent_runs = EvaluationRun.objects.select_related('evaluation_set').order_by('-start_time')[:10]
    
    total_corpora = Corpus.objects.count()
    # 统计总语料数
    messages_data = []
    storage = messages.get_messages(request)
    for message in storage:
        messages_data.append({
            'level': message.level,
            'message': str(message),
            'tags': message.tags,
        })
    
    context = {
        'evaluation_sets': evaluation_sets,
        'evaluation_sets_count': evaluation_sets.count(),
        'total_corpora': total_corpora,
        'recent_runs': recent_runs,
        'messages_data': messages_data,  # 添加处理后的消息数据
    }
    
    return render(request, 'home/index.html', context)

def run_evaluation(request):
    """
    运行评测
    """
    if request.method == 'POST':
        # 获取所有选中的评测集ID
        evaluation_set_ids = request.POST.getlist('evaluation_sets')
        api_key = request.POST.get('api_key')
        
        if not evaluation_set_ids:
            return JsonResponse({'status': 'error', 'message': '请至少选择一个评测集'})
            
        if not api_key:
            return JsonResponse({'status': 'error', 'message': '请输入API密钥'})
        
        try:
            # 验证所有选中的评测集是否存在
            evaluation_sets = EvaluationSet.objects.filter(id__in=evaluation_set_ids)
            if len(evaluation_sets) != len(evaluation_set_ids):
                return JsonResponse({'status': 'error', 'message': '请选择正确的评测集'})
        except EvaluationSet.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '请选择正确的评测集'})
        
        # 获取AI模型信息
        try:
            agent_info = AIClient(api_key).get_agent_info()
            version = agent_info.get('name', '1.0')
        except Exception as e:
            version = '1.0'  # 默认版本
        
        # 创建多个评测运行记录
        run_ids = []
        for eval_set in evaluation_sets:
            evaluation_run = EvaluationRun.objects.create(
                evaluation_set=eval_set,
                run_name=f"Run {version}",
                config={
                    "api_key": api_key,
                },
                status='running',
                version=version
            )
            run_ids.append(evaluation_run.id)
            
            # 启动异步处理线程
            thread = threading.Thread(
                target=process_dataset_async,
                args=(evaluation_run.id, eval_set.id, api_key)
            )
            thread.daemon = True  # 设置为守护线程
            thread.start()
        
        # 返回所有运行ID用于前端跟踪状态
        return JsonResponse({
            'status': 'success', 
            'message': f'已启动 {len(run_ids)} 个评测任务',
            'run_ids': run_ids  # 返回所有运行ID
        })
    
    return JsonResponse({'status': 'error', 'message': '无效的请求方法'})