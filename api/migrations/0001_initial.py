# Generated by Django 3.0.3 on 2020-02-26 09:24

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('filepath', models.FileField(upload_to='%Y/%m/%d')),
                ('filename', models.CharField(blank=True, max_length=255)),
                ('filesize', models.PositiveIntegerField(blank=True, null=True)),
                ('checksum', models.CharField(blank=True, max_length=255)),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
