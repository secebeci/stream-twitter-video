# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-04 15:22
from __future__ import unicode_literals

from django.db import migrations
import embed_video.fields


class Migration(migrations.Migration):

    dependencies = [
        ('stream_twitter', '0002_auto_20160904_1626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='video',
            field=embed_video.fields.EmbedVideoField(),
        ),
    ]
