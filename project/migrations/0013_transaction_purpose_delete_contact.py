# Generated by Django 5.1.2 on 2025-03-25 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0012_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='purpose',
            field=models.CharField(choices=[('expense', 'Expense'), ('sharing', 'Sharing'), ('food', 'Food'), ('loan', 'Loan'), ('education', 'Education'), ('other', 'Other')], default='other', max_length=20),
        ),
        migrations.DeleteModel(
            name='Contact',
        ),
    ]
