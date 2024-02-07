from django.contrib import admin

from .models import Category, Location, Post


class PostCategoryInline(admin.StackedInline):
    model = Post
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        PostCategoryInline
    ]
    list_display = [
        'title',
        'description',
        'slug',
        'is_published'
    ]
    list_filter = [
        'is_published'
    ]
    list_editable = [
        'description',
        'slug',
        'is_published'
    ]
    empty_value_display = 'Не задано'


class PostLocationInline(admin.StackedInline):
    model = Post
    extra = 0


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    inlines = [
        PostLocationInline
    ]
    list_display = [
        'name',
        'is_published',
    ]
    list_filter = [
        'is_published'
    ]
    list_editable = [
        'is_published',
    ]
    empty_value_display = 'Не задано'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'text',
        'author'
    ]
    list_filter = [
        'category',
        'is_published'
    ]
    list_editable = [
        'text',
    ]
    search_fields = [
        'text',
    ]
    empty_value_display = 'Не задано'
