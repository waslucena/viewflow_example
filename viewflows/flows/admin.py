from django.contrib import admin
from viewflow import views as viewflow
from .flows import HelloWorldFlow, PublishPollFlow, PollErrorFlow

# A HelloWorldFlow processes menus
hello_world_flow_cls = HelloWorldFlow

def hello_world_process_list_view(request, *args, **kwargs):
    kwargs['flow_cls'] = hello_world_flow_cls
    return viewflow.ProcessListView.as_view()(request, *args, **kwargs)

def hello_world_task_list_view(request, *args, **kwargs):
    kwargs['flow_cls'] = hello_world_flow_cls
    return viewflow.TaskListView.as_view()(request, *args, **kwargs)

def hello_world_queue_list_view(request, *args, **kwargs):
    kwargs['flow_cls'] = hello_world_flow_cls
    return viewflow.QueueListView.as_view()(request, *args, **kwargs)

admin.site.register_view('helloworld',       'Hellow World Processes', view=hello_world_process_list_view)
admin.site.register_view('helloworld/tasks', 'Hellow World My tasks',  view=hello_world_task_list_view)
admin.site.register_view('helloworld/queue', 'Hellow World Queue',     view=hello_world_queue_list_view)


# A PublishPollFlow processes menus
update_poll_flow_cls = PublishPollFlow

def update_poll_process_list_view(request, *args, **kwargs):
    kwargs['flow_cls'] = update_poll_flow_cls
    return viewflow.ProcessListView.as_view()(request, *args, **kwargs)

def update_poll_task_list_view(request, *args, **kwargs):
    kwargs['flow_cls'] = update_poll_flow_cls
    return viewflow.TaskListView.as_view()(request, *args, **kwargs)

def update_poll_queue_list_view(request, *args, **kwargs):
    kwargs['flow_cls'] = update_poll_flow_cls
    return viewflow.QueueListView.as_view()(request, *args, **kwargs)

admin.site.register_view('publishpoll',       'Update Poll Processes', view=update_poll_process_list_view)
admin.site.register_view('publishpoll/tasks', 'Update Poll My tasks',  view=update_poll_task_list_view)
admin.site.register_view('publishpoll/queue', 'Update Poll Queue',     view=update_poll_queue_list_view)


# All Flows processes menus
all_flow_classes = [HelloWorldFlow, PublishPollFlow, PollErrorFlow]

def all_process_list_view(request, *args, **kwargs):
    return viewflow.AllProcessListView.as_view(flow_classes=all_flow_classes)(request, *args, **kwargs)

def all_tasks_list_view(request, *args, **kwargs):
    return viewflow.AllTaskListView.as_view(flow_classes=all_flow_classes)(request, *args, **kwargs)

def all_queue_list_view(request, *args, **kwargs):
    return viewflow.AllQueueListView.as_view(flow_classes=all_flow_classes)(request, *args, **kwargs)


admin.site.register_view('workflows', 'Processes', view=all_process_list_view)
admin.site.register_view('workflows/tasks', 'My tasks', view=all_tasks_list_view)
admin.site.register_view('workflows/queue', 'Queue', view=all_queue_list_view)
