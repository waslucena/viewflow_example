from django.db import models
from viewflow.models import Process, Task


class HelloWorldProcess(Process):
    text = models.CharField(max_length=150)
    approved = models.BooleanField(default=False)

class PollProcess(Process):
    question = models.ForeignKey('polls.Question', verbose_name='Question')
    approved = models.BooleanField(default=False)

class PollErrorProcess(Process):
    question = models.ForeignKey('polls.Question', verbose_name='Question')


class PollBuildProcess(Process):
    parent_task = models.ForeignKey(Task, blank=True, null=True)
    question = models.ForeignKey('polls.Question', verbose_name='Question')
    split_count = models.IntegerField(default=0)

class ChoiceSuggestion(models.Model):
    process = models.ForeignKey(PollBuildProcess)
    task = models.ForeignKey(Task)
    choice_text = models.CharField(max_length=50)
    approved = models.BooleanField(default=False)
    selected = models.BooleanField(default=False)


class PollCreateProcess(Process):
    question = models.ForeignKey('polls.Question', verbose_name='Question')
