from django.dispatch import Signal
from viewflow import flow
from viewflow.base import this, Flow
from viewflow.views import StartProcessView, ProcessView
from viewflow.flow import flow_signal
from . import models, views
from .nodes import DynamicSplit, ExtendedIf


class HelloWorldFlow(Flow):
    process_cls = models.HelloWorldProcess

    start = flow.Start(StartProcessView, fields=["text"]) \
        .Permission(auto_create=True) \
        .Next(this.approve)

    approve = flow.View(ProcessView, fields=["approved"], task_description="Approve the request") \
        .Permission(auto_create=True) \
        .Next(this.validate_approve)

    validate_approve = flow.If(cond=lambda p: p.approved) \
        .OnTrue(this.end) \
        .OnFalse(this.end)

    end = flow.End()

StartPublishPollSignal = Signal(providing_args=["question"])

def start_publish_poll_flow(activation, **kwargs):
    activation.prepare()
    activation.process.question = kwargs['question']
    activation.done()
    return activation

class PublishPollFlow(Flow):
    process_cls = models.PollProcess

    # An example of start with a Function
    start = flow.StartFunction(start_publish_poll_flow) \
        .Next(this.approve)

    # An example of start with a Signal
    # start = flow.StartSignal(StartPublishPollSignal, start_publish_poll_flow) \
    #     .Next(this.approve)

    # An example of start with a View
    # start = flow.Start(StartProcessView, fields=["question"]) \
    #     .Permission(auto_create=True) \
    #     .Next(this.approve)

    approve = flow.View(ProcessView, fields=["approved"]) \
        .Permission(auto_create=True) \
        .Next(this.validate_approve)

    validate_approve = flow.If(cond=lambda p: p.approved) \
        .OnTrue(this.end) \
        .OnFalse(this.end)

    end = flow.End()


StartPollErrorFlowSignal = Signal(providing_args=["question", "owner"])
ResolvePollErrorFlowSignal = Signal(providing_args=["process", "owner"])

def start_poll_error_flow(activation, **kwargs):
    activation.prepare()
    if kwargs['owner']:
        activation.task.owner = kwargs['owner']
    activation.process.question = kwargs['question']
    activation.done()
    return activation

@flow_signal(task_loader=lambda flow_task, **kwargs: kwargs['process'].get_task(PollErrorFlow.resolve))
def resolve_poll_error_flow(activation, **kwargs):
    activation.prepare()
    if kwargs['owner']:
        activation.task.owner = kwargs['owner']
    activation.done()
    return activation

class PollErrorFlow(Flow):
    process_cls = models.PollErrorProcess

    start = flow.StartSignal(StartPollErrorFlowSignal, start_poll_error_flow) \
        .Next(this.resolve)

    resolve = flow.View(ProcessView, fields=[]) \
        .Permission(auto_create=True) \
        .Next(this.end)
    #
    # resolve = flow.Signal(ResolvePollErrorFlowSignal, resolve_poll_error_flow) \
    #     .Next(this.end)

    end = flow.End()


def start_build_poll_flow(activation, **kwargs):
    activation.prepare()
    activation.process.question = kwargs['question']
    activation.process.split_count = kwargs['split_count']
    activation.done()
    return activation

def create_poll(activation, **kwarg):
    from polls.models import Choice
    suggestion = models.ChoiceSuggestion.objects.get(
            process=activation.process, approved=True, selected=True)
    choice_text = suggestion.choice_text
    question = activation.process.question
    question.choice_set.add(Choice(choice_text=choice_text))
    question.save()
    return activation

def suggestion_approved(process, task):
    approve_task = task.previous.first()
    suggest_task = approve_task.previous.first()
    suggestion = models.ChoiceSuggestion.objects.get(
            process=process, task=suggest_task)
    return suggestion.approved

class BuildPollFlow(Flow):
    process_cls = models.PollBuildProcess

    start = flow.StartFunction(start_build_poll_flow) \
        .Next(this.spit)

    spit = DynamicSplit(lambda p: p.split_count) \
        .Next(this.suggest)

    suggest = flow.View(views.SuggestionView) \
        .Next(this.approve)

    approve = flow.View(views.ApproveView) \
        .Next(this.validate)

    validate = ExtendedIf(cond=suggestion_approved) \
        .OnTrue(this.join) \
        .OnFalse(this.suggest)

    join = flow.Join() \
        .Next(this.select)

    select = flow.View(views.SelectView) \
        .Next(this.build)

    build = flow.Handler(create_poll) \
        .Next(this.end)

    end = flow.End()