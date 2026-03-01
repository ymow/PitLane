"""Admin configuration for news app."""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    NewsCategory, Source, Tag, Article, Translation,
    ArticleCategory, ArticleDriver, ArticleTeam, ArticleCircuit, ArticleRace, ArticleTag
)


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'display_order', 'color')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['display_order', 'name']


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'lang', 'priority', 'is_active', 'fetch_interval',
                    'health_badge', 'consecutive_errors', 'last_success_at')
    list_filter = ('lang', 'is_active', 'is_healthy', 'priority')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('last_fetched_at', 'last_success_at', 'consecutive_errors',
                       'total_articles_fetched', 'is_healthy', 'fetch_interval')
    actions = ['reset_health']

    @admin.display(description='Health', ordering='is_healthy')
    def health_badge(self, obj):
        if obj.is_healthy and obj.consecutive_errors == 0:
            return format_html('<span style="color:green;font-weight:bold">OK</span>')
        elif obj.is_healthy:
            return format_html(
                '<span style="color:orange;font-weight:bold">WARN ({})</span>',
                obj.consecutive_errors
            )
        else:
            return format_html(
                '<span style="color:red;font-weight:bold">PAUSED ({})</span>',
                obj.consecutive_errors
            )

    @admin.action(description='Reset health (clear errors, re-enable source)')
    def reset_health(self, request, queryset):
        updated = queryset.update(consecutive_errors=0, is_healthy=True)
        self.message_user(request, f'{updated} source(s) health reset.')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class TranslationInline(admin.TabularInline):
    model = Translation
    extra = 0
    fields = ('lang', 'title', 'status', 'confidence_score')
    readonly_fields = ('confidence_score',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('original_title', 'source', 'priority', 'ingestion_status',
                    'quality_score', 'published_at', 'original_lang', 'is_published', 'is_featured')
    list_filter = ('ingestion_status', 'priority', 'source', 'original_lang',
                   'is_published', 'is_featured', 'published_at')
    search_fields = ('original_title', 'external_id')
    date_hierarchy = 'published_at'
    readonly_fields = ('ingestion_status', 'quality_score', 'simhash', 'fetched_at')
    inlines = [TranslationInline]


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('title', 'lang', 'article', 'status', 'confidence_score', 'translated_at')
    list_filter = ('lang', 'status', 'translated_at')
    search_fields = ('title', 'slug')
    date_hierarchy = 'translated_at'
