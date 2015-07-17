from django.contrib import admin
from viewflow.models import Process, Task

admin.site.unregister(Process)
admin.site.unregister(Task)
