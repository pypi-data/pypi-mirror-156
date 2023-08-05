# Generated by Django 2.2 on 2022-02-28 04:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cms', '0022_auto_20180620_1551'),
    ]

    operations = [
        migrations.CreateModel(
            name='Donate',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='donate_donate', serialize=False, to='cms.CMSPlugin')),
                ('campaign', models.CharField(max_length=255)),
                ('donation_url', models.URLField()),
                ('title', models.CharField(blank=True, max_length=255)),
                ('text', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
