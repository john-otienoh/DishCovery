from django.contrib import admin
from .models import Comment, Rating, RecipeShare, SavedRecipe

# Register your models here.
 
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("recipe", "user", "score", "created_at")
    list_filter = ("score",)
    search_fields = ("recipe__name", "user__username")
    raw_id_fields = ("recipe", "user")
 
 
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "recipe", "parent", "is_edited", "created_at")
    list_filter = ("is_edited",)
    search_fields = ("author__username", "recipe__name", "body")
    raw_id_fields = ("recipe", "author", "parent")
 
 
@admin.register(SavedRecipe)
class SavedRecipeAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "created_at")
    raw_id_fields = ("user", "recipe")
 
 
@admin.register(RecipeShare)
class RecipeShareAdmin(admin.ModelAdmin):
    list_display = ("recipe", "shared_by", "platform", "created_at")
    list_filter = ("platform",)
 