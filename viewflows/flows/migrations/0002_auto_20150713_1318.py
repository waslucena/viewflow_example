# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewflow', '0002_fsmchange'),
        ('polls', '0001_initial'),
        ('flows', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PollProcess',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='viewflow.Process', serialize=False, parent_link=True)),
                ('approved', models.BooleanField(default=False)),
                ('question', models.ForeignKey(verbose_name='Question', to='polls.Question')),
            ],
            options={
                'abstract': False,
            },
            bases=('viewflow.process',),
        ),
        migrations.DeleteModel(
            name='HelloWorldTask',
        ),
    ]
