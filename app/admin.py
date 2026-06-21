from django.contrib import admin

from app.models import Query, Result, Summary


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = ('text', 'user', 'timestamp')
    list_filter = ('user', 'timestamp')
    search_fields = ('text', 'user__username')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'query')
    search_fields = ('title', 'url')


@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ('query', 'text')
    search_fields = ('text',)
