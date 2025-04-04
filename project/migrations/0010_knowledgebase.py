# Generated by Django 5.1.1 on 2025-03-24 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0009_user_amount_user_limit'),
    ]

    operations = [
        migrations.CreateModel(
            name='KnowledgeBase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(help_text='The question to trigger the response.', max_length=255)),
                ('answer', models.TextField(help_text='The answer to provide when the question is asked.')),
            ],
        ),
    ]
