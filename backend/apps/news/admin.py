"""Admin configuration for news app."""
from django.contrib import admin
from .models import Source, Team, Driver, Tag, Article, Translation, ArticleDriver, ArticleTeam, ArticleTag


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'lang', 'priority', 'is_active', 'fetch_interval')
    list_filter = ('lang', 'is_active', 'priority')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'short_name', 'primary_color')
    search_fields = ('code', 'name', 'short_name')


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('code', 'first_name', 'last_name', 'number', 'team', 'nationality')
    list_filter = ('team', 'nationality')
    search_fields = ('code', 'first_name', 'last_name')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class TranslationInline(admin.TabularInline):
    model = Translation
    extra = 0
    fields = ('lang', 'title', 'status', 'confidence')
    readonly_fields = ('confidence',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('original_title', 'source', 'category', 'priority', 'published_at', 'original_lang')
    list_filter = ('category', 'priority', 'source', 'original_lang', 'published_at')
    search_fields = ('original_title', 'external_id')
    date_hierarchy = 'published_at'
    inlines = [TranslationInline]
    filter_horizontal = ('drivers', 'teams', 'tags')


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('title', 'lang', 'article', 'status', 'confidence', 'translated_at')
    list_filter = ('lang', 'status', 'translated_at')
    search_fields = ('title', 'slug')
    date_hierarchy = 'translated_at'
