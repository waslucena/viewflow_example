from django.db import models
from viewflow.models import Process


class HelloWorldProcess(Process):
    text = models.CharField(max_length=150)
    approved = models.BooleanField(default=False)

class PollProcess(Process):
    question = models.ForeignKey('polls.Question', verbose_name='Question')
    approved = models.BooleanField(default=False)

class PollErrorProcess(Process):
    question = models.ForeignKey('polls.Question', verbose_name='Question')
