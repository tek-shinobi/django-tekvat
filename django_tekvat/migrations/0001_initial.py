# Generated by Django 3.0.3 on 2020-02-11 12:39

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TekvatRateType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', jsonfield.fields.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='TekvatVat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_code', models.CharField(db_index=True, max_length=3)),
                ('data', jsonfield.fields.JSONField()),
            ],
        ),
    ]
