# 资源加载器 (Loader) API

`architect.utils.loader` 模块提供了资源加载功能，用于异步加载和管理游戏资源。

## 模块概述

该模块为空文件，但根据项目结构，它应该提供资源加载功能。以下是根据常见模式创建的示例实现。

## 使用示例

### 1. 基本资源加载器

```python
import threading
import time
from queue import Queue

class ResourceLoader:
    def __init__(self):
        self.loading_queue = Queue()
        self.loaded_resources = {}
        self.loading_thread = None
        self.is_loading = False
        self.callbacks = {}
    
    def load_texture(self, texture_path, on_complete=None, on_error=None):
        """加载纹理资源"""
        resource_id = f"texture_{texture_path}"
        
        if resource_id in self.loaded_resources:
            # 资源已加载，直接调用完成回调
            if on_complete:
                on_complete(self.loaded_resources[resource_id])
            return resource_id
        
        # 添加到加载队列
        self.loading_queue.put({
            'type': 'texture',
            'path': texture_path,
            'id': resource_id,
            'on_complete': on_complete,
            'on_error': on_error
        })
        
        # 启动加载线程（如果未启动）
        self.start_loading_thread()
        
        return resource_id
    
    def load_model(self, model_path, on_complete=None, on_error=None):
        """加载模型资源"""
        resource_id = f"model_{model_path}"
        
        if resource_id in self.loaded_resources:
            # 资源已加载，直接调用完成回调
            if on_complete:
                on_complete(self.loaded_resources[resource_id])
            return resource_id
        
        # 添加到加载队列
        self.loading_queue.put({
            'type': 'model',
            'path': model_path,
            'id': resource_id,
            'on_complete': on_complete,
            'on_error': on_error
        })
        
        # 启动加载线程（如果未启动）
        self.start_loading_thread()
        
        return resource_id
    
    def load_sound(self, sound_path, on_complete=None, on_error=None):
        """加载声音资源"""
        resource_id = f"sound_{sound_path}"
        
        if resource_id in self.loaded_resources:
            # 资源已加载，直接调用完成回调
            if on_complete:
                on_complete(self.loaded_resources[resource_id])
            return resource_id
        
        # 添加到加载队列
        self.loading_queue.put({
            'type': 'sound',
            'path': sound_path,
            'id': resource_id,
            'on_complete': on_complete,
            'on_error': on_error
        })
        
        # 启动加载线程（如果未启动）
        self.start_loading_thread()
        
        return resource_id
    
    def load_data(self, data_path, on_complete=None, on_error=None):
        """加载数据资源"""
        resource_id = f"data_{data_path}"
        
        if resource_id in self.loaded_resources:
            # 资源已加载，直接调用完成回调
            if on_complete:
                on_complete(self.loaded_resources[resource_id])
            return resource_id
        
        # 添加到加载队列
        self.loading_queue.put({
            'type': 'data',
            'path': data_path,
            'id': resource_id,
            'on_complete': on_complete,
            'on_error': on_error
        })
        
        # 启动加载线程（如果未启动）
        self.start_loading_thread()
        
        return resource_id
    
    def start_loading_thread(self):
        """启动加载线程"""
        if self.loading_thread is None or not self.loading_thread.is_alive():
            self.is_loading = True
            self.loading_thread = threading.Thread(target=self.loading_worker)
            self.loading_thread.daemon = True
            self.loading_thread.start()
            print("资源加载线程已启动")
    
    def loading_worker(self):
        """加载工作线程"""
        while self.is_loading:
            try:
                # 从队列获取加载任务
                task = self.loading_queue.get(timeout=0.1)
                
                try:
                    # 加载资源
                    resource = self.load_resource(task)
                    
                    # 存储加载的资源
                    self.loaded_resources[task['id']] = resource
                    
                    # 调用完成回调
                    if task['on_complete']:
                        task['on_complete'](resource)
                    
                    print(f"资源加载完成: {task['id']}")
                    
                except Exception as e:
                    print(f"资源加载失败: {task['id']}, 错误: {str(e)}")
                    
                    # 调用错误回调
                    if task['on_error']:
                        task['on_error'](str(e))
                
                # 标记任务完成
                self.loading_queue.task_done()
                
            except:
                # 队列为空，检查是否继续
                if self.loading_queue.empty():
                    time.sleep(0.1)
    
    def load_resource(self, task):
        """加载资源（模拟实现）"""
        resource_type = task['type']
        path = task['path']
        
        # 模拟加载延迟
        time.sleep(0.5)
        
        # 根据资源类型返回模拟资源
        if resource_type == 'texture':
            return {
                'type': 'texture',
                'path': path,
                'width': 256,
                'height': 256,
                'data': f"texture_data_{path}"
            }
        elif resource_type == 'model':
            return {
                'type': 'model',
                'path': path,
                'vertices': [],
                'textures': [],
                'data': f"model_data_{path}"
            }
        elif resource_type == 'sound':
            return {
                'type': 'sound',
                'path': path,
                'duration': 10.0,
                'data': f"sound_data_{path}"
            }
        elif resource_type == 'data':
            return {
                'type': 'data',
                'path': path,
                'content': f"data_content_{path}"
            }
        else:
            raise ValueError(f"未知资源类型: {resource_type}")
    
    def get_resource(self, resource_id):
        """获取已加载的资源"""
        return self.loaded_resources.get(resource_id)
    
    def unload_resource(self, resource_id):
        """卸载资源"""
        if resource_id in self.loaded_resources:
            del self.loaded_resources[resource_id]
            print(f"资源已卸载: {resource_id}")
            return True
        return False
    
    def unload_all_resources(self):
        """卸载所有资源"""
        resource_count = len(self.loaded_resources)
        self.loaded_resources.clear()
        print(f"已卸载所有 {resource_count} 个资源")
    
    def stop_loading(self):
        """停止加载"""
        self.is_loading = False
        if self.loading_thread:
            self.loading_thread.join(timeout=1.0)
        print("资源加载已停止")
    
    def wait_for_loading(self, timeout=None):
        """等待所有加载完成"""
        self.loading_queue.join()
        print("所有资源加载完成")
```

### 2. 预加载管理器

```python
class PreloadManager:
    def __init__(self):
        self.loader = ResourceLoader()
        self.preload_lists = {}
        self.preload_progress = {}
        self.on_preload_complete = None
    
    def define_preload_list(self, list_name, resources):
        """定义预加载列表"""
        self.preload_lists[list_name] = resources
        print(f"定义预加载列表: {list_name}, 包含 {len(resources)} 个资源")
    
    def start_preload(self, list_name, on_complete=None):
        """开始预加载"""
        if list_name not in self.preload_lists:
            print(f"错误: 预加载列表未找到: {list_name}")
            return
        
        self.on_preload_complete = on_complete
        
        # 初始化进度
        resources = self.preload_lists[list_name]
        self.preload_progress[list_name] = {
            'total': len(resources),
            'loaded': 0,
            'failed': 0,
            'resources': {}
        }
        
        print(f"开始预加载: {list_name}, 共 {len(resources)} 个资源")
        
        # 开始加载每个资源
        for i, resource in enumerate(resources):
            resource_id = f"{list_name}_{i}"
            
            def make_callback(res_id, res_info):
                def callback(loaded_resource):
                    self.on_resource_loaded(list_name, res_id, res_info, loaded_resource)
                return callback
            
            def make_error_callback(res_id, res_info):
                def callback(error):
                    self.on_resource_error(list_name, res_id, res_info, error)
                return callback
            
            # 根据资源类型加载
            if resource['type'] == 'texture':
                self.loader.load_texture(
                    resource['path'],
                    make_callback(resource_id, resource),
                    make_error_callback(resource_id, resource)
                )
            elif resource['type'] == 'model':
                self.loader.load_model(
                    resource['path'],
                    make_callback(resource_id, resource),
                    make_error_callback(resource_id, resource)
                )
            elif resource['type'] == 'sound':
                self.loader.load_sound(
                    resource['path'],
                    make_callback(resource_id, resource),
                    make_error_callback(resource_id, resource)
                )
            elif resource['type'] == 'data':
                self.loader.load_data(
                    resource['path'],
                    make_callback(resource_id, resource),
                    make_error_callback(resource_id, resource)
                )
    
    def on_resource_loaded(self, list_name, resource_id, resource_info, loaded_resource):
        """资源加载完成回调"""
        if list_name not in self.preload_progress:
            return
        
        progress = self.preload_progress[list_name]
        progress['loaded'] += 1
        progress['resources'][resource_id] = {
            'info': resource_info,
            'resource': loaded_resource,
            'status': 'loaded'
        }
        
        # 计算进度百分比
        percentage = (progress['loaded'] / progress['total']) * 100
        print(f"预加载进度: {list_name} - {progress['loaded']}/{progress['total']} ({percentage:.1f}%)")
        
        # 检查是否全部完成
        if progress['loaded'] + progress['failed'] >= progress['total']:
            self.on_preload_list_complete(list_name)
    
    def on_resource_error(self, list_name, resource_id, resource_info, error):
        """资源加载错误回调"""
        if list_name not in self.preload_progress:
            return
        
        progress = self.preload_progress[list_name]
        progress['failed'] += 1
        progress['resources'][resource_id] = {
            'info': resource_info,
            'error': error,
            'status': 'failed'
        }
        
        print(f"资源加载失败: {resource_id}, 错误: {error}")
        
        # 计算进度百分比
        total_processed = progress['loaded'] + progress['failed']
        percentage = (total_processed / progress['total']) * 100
        print(f"预加载进度: {list_name} - {total_processed}/{progress['total']} ({percentage:.1f}%)")
        
        # 检查是否全部完成
        if total_processed >= progress['total']:
            self.on_preload_list_complete(list_name)
    
    def on_preload_list_complete(self, list_name):
        """预加载列表完成"""
        if list_name not in self.preload_progress:
            return
        
        progress = self.preload_progress[list_name]
        
        print(f"预加载完成: {list_name}")
        print(f"  成功: {progress['loaded']}")
        print(f"  失败: {progress['failed']}")
        print(f"  总计: {progress['total']}")
        
        # 调用完成回调
        if self.on_preload_complete:
            self.on_preload_complete(list_name, progress)
    
    def get_preload_progress(self, list_name):
        """获取预加载进度"""
        if list_name in self.preload_progress:
            progress = self.preload_progress[list_name]
            total_processed = progress['loaded'] + progress['failed']
            return {
                'loaded': progress['loaded'],
                'failed': progress['failed'],
                'total': progress['total'],
                'percentage': (total_processed / progress['total']) * 100 if progress['total'] > 0 else 0
            }
        return None
    
    def get_loaded_resource(self, list_name, resource_index):
        """获取已加载的资源"""
        if list_name in self.preload_progress:
            resource_id = f"{list_name}_{resource_index}"
            if resource_id in self.preload_progress[list_name]['resources']:
                resource_data = self.preload_progress[list_name]['resources'][resource_id]
                if resource_data['status'] == 'loaded':
                    return resource_data['resource']
        return None
    
    def clear_preload_list(self, list_name):
        """清空预加载列表"""
        if list_name in self.preload_lists:
            del self.preload_lists[list_name]
        
        if list_name in self.preload_progress:
            del self.preload_progress[list_name]
        
        print(f"清空预加载列表: {list_name}")
```

### 3. 场景资源管理器

```python
class SceneResourceManager:
    def __init__(self):
        self.loader = ResourceLoader()
        self.scene_resources = {}
        self.current_scene = None
        self.scene_transition_resources = {}
    
    def register_scene_resources(self, scene_name, resources):
        """注册场景资源"""
        self.scene_resources[scene_name] = resources
        print(f"注册场景资源: {scene_name}, 包含 {len(resources)} 个资源")
    
    def load_scene_resources(self, scene_name, on_progress=None, on_complete=None):
        """加载场景资源"""
        if scene_name not in self.scene_resources:
            print(f"错误: 场景资源未注册: {scene_name}")
            if on_complete:
                on_complete(False)
            return
        
        self.current_scene = scene_name
        resources = self.scene_resources[scene_name]
        
        print(f"开始加载场景资源: {scene_name}")
        
        # 创建加载任务
        load_tasks = []
        loaded_count = 0
        total_count = len(resources)
        
        def on_resource_loaded(resource_info, resource):
            nonlocal loaded_count
            loaded_count += 1
            
            # 更新进度
            if on_progress:
                percentage = (loaded_count / total_count) * 100
                on_progress(percentage, loaded_count, total_count)
            
            print(f"场景资源加载: {loaded_count}/{total_count} ({percentage:.1f}%)")
            
            # 检查是否全部完成
            if loaded_count >= total_count:
                print(f"场景资源加载完成: {scene_name}")
                if on_complete:
                    on_complete(True)
        
        def on_resource_error(resource_info, error):
            nonlocal loaded_count
            loaded_count += 1
            
            print(f"场景资源加载失败: {resource_info['path']}, 错误: {error}")
            
            # 更新进度
            if on_progress:
                percentage = (loaded_count / total_count) * 100
                on_progress(percentage, loaded_count, total_count)
            
            # 检查是否全部完成
            if loaded_count >= total_count:
                print(f"场景资源加载完成（有失败）: {scene_name}")
                if on_complete:
                    on_complete(False)
        
        # 开始加载每个资源
        for resource in resources:
            if resource['type'] == 'texture':
                self.loader.load_texture(
                    resource['path'],
                    lambda res, ri=resource: on_resource_loaded(ri, res),
                    lambda err, ri=resource: on_resource_error(ri, err)
                )
            elif resource['type'] == 'model':
                self.loader.load_model(
                    resource['path'],
                    lambda res, ri=resource: on_resource_loaded(ri, res),
                    lambda err, ri=resource: on_resource_error(ri, err)
                )
            elif resource['type'] == 'sound':
                self.loader.load_sound(
                    resource['path'],
                    lambda res, ri=resource: on_resource_loaded(ri, res),
                    lambda err, ri=resource: on_resource_error(ri, err)
                )
            elif resource['type'] == 'data':
                self.loader.load_data(
                    resource['path'],
                    lambda res, ri=resource: on_resource_loaded(ri, res),
                    lambda err, ri=resource: on_resource_error(ri, err)
                )
    
    def unload_scene_resources(self, scene_name):
        """卸载场景资源"""
        if scene_name not in self.scene_resources:
            return
        
        # 获取场景资源列表
        resources = self.scene_resources[scene_name]
        
        # 卸载每个资源
        for i, resource in enumerate(resources):
            resource_id = f"{scene_name}_{i}"
            self.loader.unload_resource(resource_id)
        
        print(f"卸载场景资源: {scene_name}")
    
    def unload_current_scene_resources(self):
        """卸载当前场景资源"""
        if self.current_scene:
            self.unload_scene_resources(self.current_scene)
            self.current_scene = None
    
    def preload_next_scene(self, next_scene_name):
        """预加载下一个场景资源"""
        if next_scene_name not in self.scene_resources:
            print(f"错误: 下一个场景资源未注册: {next_scene_name}")
            return
        
        # 获取当前场景和下一个场景的资源
        current_resources = self.scene_resources.get(self.current_scene, [])
        next_resources = self.scene_resources[next_scene_name]
        
        # 找出需要预加载的资源（不在当前场景中的资源）
        preload_resources = []
        
        for