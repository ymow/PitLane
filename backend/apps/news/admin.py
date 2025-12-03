"""Admin configuration for news app."""
from django.contrib import admin
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
    list_display = ('name', 'slug', 'lang', 'priority', 'is_active', 'fetch_interval')
    list_filter = ('lang', 'is_active', 'priority')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


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
    list_display = ('original_title', 'source', 'priority', 'published_at', 'original_lang', 'is_published', 'is_featured')
    list_filter = ('priority', 'source', 'original_lang', 'is_published', 'is_featured', 'published_at')
    search_fields = ('original_title', 'external_id')
    date_hierarchy = 'published_at'
    inlines = [TranslationInline]


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('title', 'lang', 'article', 'status', 'confidence_score', 'translated_at')
    list_filter = ('lang', 'status', 'translated_at')
    search_fields = ('title', 'slug')
    date_hierarchy = 'translated_at'
