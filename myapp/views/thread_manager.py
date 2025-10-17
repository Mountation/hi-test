# myapp/thread_manager.py
import threading
from collections import defaultdict
from django.core.cache import cache

class TestSetThreadManager:
    def __init__(self):
        self.running_threads = {}
        self.thread_lock = threading.Lock()
    
    def add_thread(self, run_id, thread):
        """添加线程到管理器"""
        with self.thread_lock:
            self.running_threads[run_id] = {
                'thread': thread,
                'start_time': threading.get_time(),
                'status': 'running'
            }
    
    def remove_thread(self, run_id):
        """从管理器移除线程"""
        with self.thread_lock:
            if run_id in self.running_threads:
                del self.running_threads[run_id]
    
    def get_thread_status(self, run_id):
        """获取特定线程状态"""
        with self.thread_lock:
            return self.running_threads.get(run_id, None)
    
    def get_all_threads(self):
        """获取所有线程状态"""
        with self.thread_lock:
            return self.running_threads.copy()

# 全局实例
thread_manager = TestSetThreadManager()