from django.db import models
from django.db.models.signals import post_save
from ..flows.flows import StartPollErrorFlowSignal, ResolvePollErrorFlowSignal, PollErrorFlow

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

class Choice(models.Model):
    question = models.ForeignKey(Question)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

def some_hook(sender, instance, **kwargs):
    try:
        process = PollErrorFlow.process_cls.objects.get(question=instance, status='NEW')
    except PollErrorFlow.process_cls.DoesNotExist:
        process = None
    if 'cool' not in instance.question_text:
        if not process:
            StartPollErrorFlowSignal.send(sender=Question.__class__, question=instance)
    else:
        if process:
            ResolvePollErrorFlowSignal.send(sender=Question.__class__, process=process)

post_save.connect(some_hook, sender=Question)