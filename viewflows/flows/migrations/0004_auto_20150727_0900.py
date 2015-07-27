# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
        ('viewflow', '0002_fsmchange'),
        ('flows', '0003_auto_20150715_1414'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChoiceSuggestion',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('choice_text', models.CharField(max_length=50)),
                ('approved', models.BooleanField(default=False)),
                ('selected', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='PollBuildProcess',
            fields=[
                ('process_ptr', models.OneToOneField(serialize=False, parent_link=True, to='viewflow.Process', auto_created=True, primary_key=True)),
                ('split_count', models.IntegerField(default=0)),
                ('question', models.ForeignKey(verbose_name='Question', to='polls.Question')),
            ],
            options={
                'abstract': False,
            },
            bases=('viewflow.process',),
        ),
        migrations.AddField(
            model_name='choicesuggestion',
            name='process',
            field=models.ForeignKey(to='flows.PollBuildProcess'),
        ),
        migrations.AddField(
            model_name='choicesuggestion',
            name='task',
            field=models.ForeignKey(to='viewflow.Task'),
        ),
    ]
