# Generated by Django 4.0.4 on 2022-04-20 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('account_number', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('balance', models.PositiveBigIntegerField()),
            ],
        ),
    ]