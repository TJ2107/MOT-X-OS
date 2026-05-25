from motx_os_bridge.plugins.eye_tracking_integrated import IntegratedEyeTracking
obj = IntegratedEyeTracking()
print('has face_mesh:', hasattr(obj,'face_mesh'), 'value:', getattr(obj,'face_mesh',None))
print('has tasks_detector:', hasattr(obj,'tasks_detector'), 'value:', getattr(obj,'tasks_detector',None))
print('use_tasks_api:', getattr(obj,'use_tasks_api',None))
