from django.dispatch import Signal
from viewflow import flow
from viewflow.base import this, Flow
from viewflow.views import StartProcessView, ProcessView
from viewflow.flow import flow_signal
from . import models


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