from django.contrib import admin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from .models import Choice, Question

from django_object_actions import DjangoObjectActions
from ..flows.flows import PublishPollFlow, HelloWorldFlow

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ['question_text']
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
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

    objectactions = ('publish_this', 'hello_world')

admin.site.register(Question, QuestionAdmin)