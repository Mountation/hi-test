# myapp/views/evaluation.py
import logging
from django.shortcuts import render
from django.http import JsonResponse
from ..models import EvaluationSet, Corpus, EvaluationRun, CorpusResult
from ..AIClient import AIClient
from ..AIEval import AIEval
from django.utils import timezone
import time
from django.core.cache import cache
import json

# 配置日志记录器
logger = logging.getLogger(__name__)

def get_processing_status(run_id):
    """从缓存中获取处理状态"""
    status_json = cache.get(f'processing_status_{run_id}')
    if status_json:
        return json.loads(status_json)
    return None

def set_processing_status(run_id, status_data):
    """将处理状态保存到缓存中"""
    cache.set(f'processing_status_{run_id}', json.dumps(status_data), timeout=3600)  # 1小时超时

def process_dataset_async(run_id, evaluation_set_id, api_key):
    """
    异步处理数据库中的数据集
    """
    status_data = {
        'status': 'processing',
        'processed': 0,
        'total': 0,
        'data': [],
        'error': None,
        'evaluation_set_id': evaluation_set_id,
    }
    set_processing_status(run_id, status_data)
    
    logger.info('Starting process_dataset_async run_id=%s evaluation_set_id=%s', run_id, evaluation_set_id)
    try:
        # 获取评测集和语料
        evaluation_set = EvaluationSet.objects.get(id=evaluation_set_id)
        corpora = Corpus.objects.filter(evaluation_set=evaluation_set)
        
        # 获取评测运行记录
        evaluation_run = EvaluationRun.objects.get(id=run_id)
        
        status_data['total'] = corpora.count()
        status_data['evaluation_set_name'] = evaluation_set.name
        status_data['corpus_count'] = corpora.count()
        status_data['start_time'] = evaluation_run.start_time.strftime('%Y-%m-%d %H:%M:%S')
        set_processing_status(run_id, status_data)
        
        # 更新运行状态为运行中
        evaluation_run.status = 'running'
        evaluation_run.save()
        
        excel_data = []
        ai_client = AIClient(api_key=api_key)
        
        # 获取AI模型版本信息，添加错误处理
        try:
            agent_info = ai_client.get_agent_info()
            version = agent_info.get('name', '1.0')  # 如果没有name字段，使用默认值
            logger.info('AI agent info for run_id=%s: %s', run_id, agent_info)
        except Exception as e:
            logger.exception('Failed to get AI agent info for run_id=%s: %s', run_id, e)
            version = '1.0'  # 默认版本
            
        ai_eval = AIEval()
        
        start_process_time = time.time()
        
        for i, corpus in enumerate(corpora):
            try:
                # 调用AI接口获取结果
                result = ai_client.get_res_hotline_testenv(corpus.content)
                
                # 获取预期响应
                expected_response = corpus.expected_response or ""
                
                # 评估结果
                score_text = ai_eval.eval_ai(corpus.content, result, expected_response)
                
                # 尝试从评分文本中提取数值
                try:
                    # 简单的数值提取逻辑，您可以根据实际评分格式进行调整
                    import re
                    score_match = re.search(r'(\d+\.?\d*)', score_text)
                    score = float(score_match.group(1)) if score_match else 0.0
                except:
                    score = 0.0
                
                # 保存结果到数据库，使用获取到的版本信息
                corpus_result = CorpusResult.objects.create(
                    evaluation_run=evaluation_run,
                    corpus=corpus,
                    actual_response=result,
                    score=score,
                    status='success',
                    version=version,  # 使用从API获取的版本
                    execution_order=i+1
                )
                
                # 构造前端显示数据
                row_data = {
                    'content': corpus.content,
                    'expected_response': expected_response,
                    'actual_response': result,
                    'score': score,
                    'corpus_type': corpus.intent or '',
                    'created_at': corpus.created_at.strftime('%Y-%m-%d %H:%M:%S') if corpus.created_at else '',
                    'version': version,  # 使用从API获取的版本
                }
                excel_data.append(row_data)
                
                # 更新进度
                status_data['processed'] = i + 1
                set_processing_status(run_id, status_data)
                
            except Exception as e:
                # 保存失败结果
                CorpusResult.objects.create(
                    evaluation_run=evaluation_run,
                    corpus=corpus,
                    actual_response="",
                    score=None,
                    status='failed',
                    error_msg=str(e),
                    version=version,  # 使用从API获取的版本
                    execution_order=i+1
                )
                logger.exception('Error processing corpus id=%s run_id=%s: %s', getattr(corpus, 'id', None), run_id, e)
                # 不再抛出异常，继续处理下一条语料
                continue
        
        # 更新运行完成状态，使用获取到的版本信息
        evaluation_run.end_time = timezone.now()
        evaluation_run.duration = round(time.time() - start_process_time, 3)
        evaluation_run.status = 'success'
        evaluation_run.summary_metrics = {
            'total_processed': len(excel_data),
            'success_count': len(excel_data),
            'failed_count': status_data['total'] - len(excel_data)
        }
        evaluation_run.version = version  # 使用从API获取的版本
        evaluation_run.save()
        
        status_data.update({
            'status': 'completed',
            'data': excel_data,
            'end_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        logger.info('Completed process_dataset_async run_id=%s processed=%d', run_id, len(excel_data))
        set_processing_status(run_id, status_data)
        
        # 任务完成后，设置一个较短的过期时间
        cache.set(f'processing_status_{run_id}', json.dumps(status_data), timeout=300)  # 5分钟超时
        
    except Exception as e:
        # 更新运行失败状态
        if 'evaluation_run' in locals():
            evaluation_run.end_time = timezone.now()
            evaluation_run.status = 'failed'
            evaluation_run.summary_metrics = {'error': str(e)}
            # 如果version已定义，使用它；否则使用默认值
            evaluation_run.version = version if 'version' in locals() else '1.0'
            evaluation_run.save()
            
        status_data.update({
            'status': 'failed',
            'error': str(e),
            'end_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        logger.exception('process_dataset_async failed run_id=%s: %s', run_id, e)
        set_processing_status(run_id, status_data)
        
        # 失败任务也设置较短的过期时间
        cache.set(f'processing_status_{run_id}', json.dumps(status_data), timeout=300)  # 5分钟超时

def check_processing_status(request):
    """
    检查数据库数据集处理进度的API端点
    """
    run_id = request.GET.get('run_id')
    if run_id:
        status = get_processing_status(run_id)
        if status:
            return JsonResponse(status)
    
    return JsonResponse({'status': 'not_found'})

def cancel_processing(request):
    """
    取消正在进行的处理任务
    """
    if request.method == 'POST':
        run_id = request.POST.get('run_id')
        if run_id:
            status = get_processing_status(run_id)
            if status:
                status['cancelled'] = True
                status['status'] = 'cancelled'
                set_processing_status(run_id, status)
                return JsonResponse({'status': 'success', 'message': '任务已取消'})
        
        return JsonResponse({'status': 'error', 'message': '未找到任务'})
    
    return JsonResponse({'status': 'error', 'message': '无效的请求方法'})