from django.dispatch import Signal
from viewflow import flow
from viewflow.base import this, Flow
from viewflow.views import StartProcessView, ProcessView
from . import models


class HelloWorldFlow(Flow):
    process_cls = models.HelloWorldProcess

    start = flow.Start(StartProcessView, fields=["text"]) \
        .Permission(auto_create=True) \
        .Next(this.approve)

    approve = flow.View(ProcessView, fields=["approved"]) \
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