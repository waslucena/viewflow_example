# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewflow', '0002_fsmchange'),
        ('polls', '0001_initial'),
        ('flows', '0004_auto_20150727_0900'),
    ]

    operations = [
        migrations.CreateModel(
            name='PollCreateProcess',
            fields=[
                ('process_ptr', models.OneToOneField(primary_key=True, to='viewflow.Process', serialize=False, parent_link=True, auto_created=True)),
                ('question', models.ForeignKey(to='polls.Question', verbose_name='Question')),
            ],
            options={
                'abstract': False,
            },
            bases=('viewflow.process',),
        ),
    ]
