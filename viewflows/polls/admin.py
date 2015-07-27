from django.contrib import admin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from .models import Choice, Question

from django_object_actions import DjangoObjectActions
from flows.flows import PublishPollFlow, HelloWorldFlow
from flows.flows import StartPollErrorFlowSignal, ResolvePollErrorFlowSignal,\
    PollErrorFlow, BuildPollFlow

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0
    readonly_fields = ['choice_text', 'votes']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class QuestionAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ['question_text']
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date']}),
    ]
    inlines = [ChoiceInline]

    def publish_this(self, request, obj):
        # Can also work with Signals, if the flow supports it
        # from ..flows.flows import StartPublishPollSignal
        # StartPublishPollSignal.send(sender=self.__class__, question=obj)

        activation = PublishPollFlow.start.run(question=obj)
        process = activation.process

        process_url = reverse('{}:details'.format(process.flow_cls.instance.namespace), kwargs={'process_pk': process.pk})
        message = 'Publish Poll Process <a href="{}">{}</a> has started'.format(process_url, process.pk)
        messages.add_message(request, messages.SUCCESS, mark_safe(message))
    publish_this.label = "Publish"
    publish_this.short_description = "Start Publish Poll process"

    def hello_world(self, request, obj):
        task = HelloWorldFlow.start
        args = [HelloWorldFlow, task]
        kwargs = {}
        return task.view(request, *args, **kwargs)
    hello_world.label = "Hello"
    hello_world.short_description = "Start Hello World process"

    def build_this(self, request, obj):
        activation = BuildPollFlow.start.run(question=obj, split_count=3)
        process = activation.process

        process_url = reverse('{}:details'.format(process.flow_cls.instance.namespace), kwargs={'process_pk': process.pk})
        message = 'Build Poll Process <a href="{}">{}</a> has started'.format(process_url, process.pk)
        messages.add_message(request, messages.SUCCESS, mark_safe(message))
    build_this.label = "Build"
    build_this.short_description = "Start Build Poll process"

    objectactions = ('publish_this', 'hello_world', 'build_this')

    def save_model(self, request, obj, form, change):
        super(QuestionAdmin, self).save_model(request, obj, form, change)
        try:
            process = PollErrorFlow.process_cls.objects.get(question=obj, status='NEW')
        except PollErrorFlow.process_cls.DoesNotExist:
            process = None
        if 'cool' not in obj.question_text:
            if not process:
                StartPollErrorFlowSignal.send(sender=Question.__class__, question=obj, owner=request.user)
        else:
            if process:
                task = process.get_task(PollErrorFlow.resolve)
                activation = task.activate()
                activation.prepare()
                activation.done()
                # ResolvePollErrorFlowSignal.send(sender=Question.__class__, process=process, owner=request.user)

admin.site.register(Question, QuestionAdmin)