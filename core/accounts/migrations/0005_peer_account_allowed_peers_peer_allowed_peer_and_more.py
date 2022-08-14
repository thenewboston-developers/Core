# Generated by Django 4.0.6 on 2022-08-14 23:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_remove_account_avatar_remove_account_display_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Peer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='allowed_peers',
            field=models.ManyToManyField(
                related_name='allowing_peers', through='accounts.Peer', to='accounts.account'
            ),
        ),
        migrations.AddField(
            model_name='peer',
            name='allowed_peer',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='allowed_peer', to='accounts.account'
            ),
        ),
        migrations.AddField(
            model_name='peer',
            name='allowing_peer',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='allowing_peer', to='accounts.account'
            ),
        ),
        migrations.AddConstraint(
            model_name='peer',
            constraint=models.UniqueConstraint(fields=('allowing_peer', 'allowed_peer'), name='unique_peer_relation'),
        ),
    ]
