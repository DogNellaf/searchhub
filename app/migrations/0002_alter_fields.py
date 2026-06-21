from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='query',
            options={
                'ordering': ['-timestamp'],
                'verbose_name': 'Поисковой запрос',
                'verbose_name_plural': 'Поисковые запросы',
            },
        ),
        migrations.AlterModelOptions(
            name='result',
            options={
                'verbose_name': 'Результат поискового запроса',
                'verbose_name_plural': 'Результаты поисковых запросов',
            },
        ),
        migrations.AlterModelOptions(
            name='summary',
            options={
                'verbose_name': 'Краткий пересказ',
                'verbose_name_plural': 'Краткие пересказы',
            },
        ),
        migrations.AlterField(
            model_name='query',
            name='text',
            field=models.CharField(db_index=True, max_length=500, verbose_name='Текст'),
        ),
        migrations.AlterField(
            model_name='query',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания'),
        ),
        migrations.AlterField(
            model_name='result',
            name='description',
            field=models.TextField(verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='result',
            name='title',
            field=models.CharField(max_length=500, verbose_name='Заголовок'),
        ),
        migrations.AlterField(
            model_name='result',
            name='url',
            field=models.URLField(max_length=2000, verbose_name='Ссылка'),
        ),
        migrations.AlterField(
            model_name='summary',
            name='text',
            field=models.TextField(verbose_name='Текст'),
        ),
    ]
