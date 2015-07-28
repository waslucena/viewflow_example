from viewflow.activation import AbstractGateActivation
from viewflow.flow import base
from viewflow.flow import gates
from viewflow.token import Token
from viewflow.views import StartProcessView

import traceback

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db import transaction
from django.utils.timezone import now

from viewflow import signals
from viewflow.activation import Activation, STATUS, context


class DynamicSplitActivation(AbstractGateActivation):
    def calculate_next(self):
        self._split_count = self.flow_task._task_count_callback(self.process)

    def activate_next(self):
        if self._split_count:
            token_source = Token.split_token_source(self.task.token, self.task.pk)
            for _ in range(self._split_count):
                self.flow_task._next.activate(prev_activation=self, token=next(token_source))


class DynamicSplit(base.NextNodeMixin,
                   base.UndoViewMixin,
                   base.CancelViewMixin,
                   base.PerformViewMixin,
                   base.DetailsViewMixin,
                   base.Gateway):
    """
    Activates several outgoing task instances depends on callback value
    Example::
        spit_on_decision = flow.DynamicSplit(lambda p: 4) \\
            .Next(this.make_decision)
        make_decision = flow.View(MyView) \\
            .Next(this.join_on_decision)
        join_on_decision = flow.Join() \\
            .Next(this.end)
    """
    task_type = 'SPLIT'
    activation_cls = DynamicSplitActivation

    def __init__(self, callback):
        super(DynamicSplit, self).__init__()
        self._task_count_callback = callback



class ExtendedIfActivation(gates.IfActivation):
    def calculate_next(self):
        self.condition_result = self.flow_task.condition(self.process, self.task)

class ExtendedIf(gates.If):
    task_type = 'EIF'
    activation_cls = ExtendedIfActivation



class SubprocessActivation(Activation):
    @Activation.status.transition(source=STATUS.NEW, target=STATUS.STARTED)
    def start(self):
        try:
            with transaction.atomic(savepoint=True):
                self.task.started = now()
                self.task.save()

                signals.task_started.send(sender=self.flow_cls, process=self.process, task=self.task)

                kwargs = self.flow_task.kwargs_source(self.process)
                kwargs['parent_task'] = self.task
                self.flow_task.start_handler.run(**kwargs)

        except Exception as exc:
            if not context.propagate_exception:
                self.task.comments = "{}\n{}".format(exc, traceback.format_exc())
                self.task.finished = now()
                self.set_status(STATUS.ERROR)
                self.task.save()
                signals.task_failed.send(sender=self.flow_cls, process=self.process, task=self.task)
            else:
                raise

    @Activation.status.transition(source=STATUS.STARTED, target=STATUS.DONE)
    def done(self):
        """
        Mark task as done

        .. seealso::
            :data:`viewflow.signals.task_finished`

        """
        self.task.finished = now()
        self.set_status(STATUS.DONE)
        self.task.save()

        signals.task_finished.send(sender=self.flow_cls, process=self.process, task=self.task)

        self.activate_next()

    @Activation.status.transition(source=STATUS.DONE)
    def activate_next(self):
        """Activate all outgoing edges."""
        self.flow_task._next.activate(prev_activation=self, token=self.task.token)


    @classmethod
    def activate(cls, flow_task, prev_activation, token):
        flow_cls, flow_task = flow_task.flow_cls, flow_task
        process = prev_activation.process

        task = flow_cls.task_cls(
            process=process,
            flow_task=flow_task,
            token=token)

        task.save()
        task.previous.add(prev_activation.task)

        activation = cls()
        activation.initialize(flow_task, task)

        activation.start()

        return activation

class Subprocess(base.NextNodeMixin, base.DetailsViewMixin, base.Gateway):
    task_type = 'SUBPROCESS'
    activation_cls = SubprocessActivation

    def __init__(self, start_handler, kwargs_source):
        super(Subprocess, self).__init__()
        self.start_handler = start_handler
        self.kwargs_source = kwargs_source

    def on_flow_finished(self, **signal_kwargs):
        process = signal_kwargs['process']

        if process.parent_task:
            activation = process.parent_task.activate()
            activation.done()

    def ready(self):
        signals.flow_finished.connect(self.on_flow_finished, sender=self.start_handler.flow_cls)


class StartAdminView(StartProcessView):
    def __init__(self, *args, **kwargs):
        self.model = kwargs['model']
        super(StartAdminView, self).__init__()

    def get(self, request, *args, **kwargs):
        url = reverse(
            'admin:{}_{}_add'.format(
                self.model._meta.app_label, self.model.__name__.lower()
            )
        )
        return HttpResponseRedirect(url)
