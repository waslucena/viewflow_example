# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewflow', '0002_fsmchange'),
        ('polls', '0001_initial'),
        ('flows', '0002_auto_20150713_1318'),
    ]

    operations = [
        migrations.CreateModel(
            name='PollErrorProcess',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, serialize=False, to='viewflow.Process', primary_key=True, parent_link=True)),
                ('question', models.ForeignKey(verbose_name='Question', to='polls.Question')),
            ],
            options={
                'abstract': False,
            },
            bases=('viewflow.process',),
        ),
        migrations.AlterField(
            model_name='helloworldprocess',
            name='text',
            field=models.CharField(max_length=150),
        ),
    ]
