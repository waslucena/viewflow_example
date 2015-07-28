from django.views import generic
from django.http import HttpResponseRedirect

from viewflow.views import task
from viewflow import flow

from . import models
from polls.models import Question

class SuggestionView(task.TaskViewMixin, generic.CreateView):
    model = models.ChoiceSuggestion
    fields = ['choice_text']

    def form_valid(self, form):
        self.object = form.save(commit=False)

        self.object.process = self.activation.process
        self.object.task = self.activation.task
        self.object.save()

        self.activation.done()
        self.message_complete()

        return HttpResponseRedirect(self.get_success_url())


class ApproveView(task.TaskViewMixin, generic.UpdateView):
    model = models.ChoiceSuggestion
    fields = ['choice_text', 'approved']

    def get_object(self):
        previous_tasks = self.activation.task.previous
        previous_task = previous_tasks.first()
        return models.ChoiceSuggestion.objects.get(
            process=self.activation.process, task=previous_task)

    def form_valid(self, form):
        self.object = form.save(commit=False)

        self.object.save()

        self.activation.done()
        self.message_complete()

        return HttpResponseRedirect(self.get_success_url())

from django import forms
from django.views.generic.edit import FormView


class SelectChoiceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        choices = kwargs['choices']
        del kwargs['choices']
        super(SelectChoiceForm, self).__init__(*args, **kwargs)
        self.fields['selected'] = forms.ChoiceField(choices=choices, widget=forms.RadioSelect())


class SelectView(task.TaskViewMixin, FormView):
    def get_form(self):
        choices = models.ChoiceSuggestion.objects.filter(
            process=self.activation.process, approved=True)
        choices = [(choice.id, choice.choice_text) for choice in choices]
        return SelectChoiceForm(choices=choices)

    def post(self, request, *args, **kwargs):
        selected_choice = int(request.POST['selected'])
        choices = models.ChoiceSuggestion.objects.filter(
            process=self.activation.process, approved=True)
        for choice in choices:
            choice.selected = selected_choice == choice.id
            choice.save()

        self.activation.done()
        self.message_complete()

        return HttpResponseRedirect(self.get_success_url())
