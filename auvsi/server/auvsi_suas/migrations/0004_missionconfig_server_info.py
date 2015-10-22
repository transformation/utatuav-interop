# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from auvsi_suas.models.server_info import ServerInfo


class Migration(migrations.Migration):

    dependencies = [('auvsi_suas', '0003_missionconfig_is_active')]

    operations = [
        migrations.AddField(
            model_name='missionconfig',
            name='server_info',
            field=models.ForeignKey(
                default=1,
                to='auvsi_suas.ServerInfo'),
            preserve_default=False),
    ]
