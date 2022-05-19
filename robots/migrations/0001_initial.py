# Generated by Django 4.0.3 on 2022-03-27 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Эл почта')),
            ],
        ),
        migrations.CreateModel(
            name='Robots',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=50, verbose_name='Имя')),
                ('info', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
                ('folder_id', models.IntegerField(blank=True, null=True, verbose_name='id папки')),
                ('process_key', models.CharField(blank=True, max_length=100, null=True, verbose_name='Ключ процесса')),
                ('robot_id', models.IntegerField(blank=True, null=True, verbose_name='id робота')),
                ('email', models.ManyToManyField(to='robots.email')),
            ],
            options={
                'verbose_name': 'Робот',
                'verbose_name_plural': 'Роботы',
            },
        ),
    ]
