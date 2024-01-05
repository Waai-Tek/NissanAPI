# Generated by Django 5.0 on 2024-01-05 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BaseJourney',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=255)),
                ('JourneyDescription', models.TextField(blank=True, null=True)),
                ('CreatedOn', models.DateTimeField()),
                ('ModifiedOn', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
