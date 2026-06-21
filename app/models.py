from django.db import models
from django.contrib.auth.models import User


class Query(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='queries')
    text = models.CharField('Текст', max_length=500, db_index=True)
    timestamp = models.DateTimeField('Дата и время создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Поисковой запрос'
        verbose_name_plural = 'Поисковые запросы'
        ordering = ['-timestamp']

    def __str__(self):
        return self.text


class Result(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name='results')
    title = models.CharField('Заголовок', max_length=500)
    url = models.URLField('Ссылка', max_length=2000)
    description = models.TextField('Описание')

    class Meta:
        verbose_name = 'Результат поискового запроса'
        verbose_name_plural = 'Результаты поисковых запросов'

    def __str__(self):
        return self.title


class Summary(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name='summaries')
    text = models.TextField('Текст')

    class Meta:
        verbose_name = 'Краткий пересказ'
        verbose_name_plural = 'Краткие пересказы'

    def __str__(self):
        return self.text[:50]
