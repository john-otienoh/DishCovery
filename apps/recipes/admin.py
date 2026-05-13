from django.contrib import admin
from .models import Tag, MealType, Recipe

# Register your models here.
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "cuisine", "difficulty", "rating", "review_count", "is_published", "created_at")
    list_filter = ("difficulty", "cuisine", "is_published", "meal_types")
    search_fields = ("name", "cuisine", "author__username")
    filter_horizontal = ("tags", "meal_types")
    raw_id_fields = ("author",)
    readonly_fields = ("rating", "review_count", "created_at", "updated_at")
    ordering = ("-created_at",)
 
 
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
 
 
@admin.register(MealType)
class MealTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
 