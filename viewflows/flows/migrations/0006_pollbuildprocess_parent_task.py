# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewflow', '0002_fsmchange'),
        ('flows', '0005_pollcreateprocess'),
    ]

    operations = [
        migrations.AddField(
            model_name='pollbuildprocess',
            name='parent_task',
            field=models.ForeignKey(to='viewflow.Task', blank=True, null=True),
        ),
    ]
