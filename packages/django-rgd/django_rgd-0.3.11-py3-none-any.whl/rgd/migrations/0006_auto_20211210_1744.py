# Generated by Django 3.2.10 on 2021-12-10 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rgd', '0005_auto_20211105_1715'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='name',
            field=models.CharField(max_length=127, unique=True),
        ),
        migrations.AddConstraint(
            model_name='checksumfile',
            constraint=models.UniqueConstraint(
                fields=('collection', 'url'), name='unique_url_collection'
            ),
        ),
    ]
