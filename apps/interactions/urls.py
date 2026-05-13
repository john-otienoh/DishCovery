from django.urls import path

from .views import (
    CommentDetailView,
    RecipeCommentListCreateView,
    RecipeRatingListView,
    RecipeRatingView,
    RecipeSaveToggleView,
    RecipeShareView,
    SavedRecipeListView,
)

urlpatterns = [
    path("recipes/<int:recipe_id>/rate/", RecipeRatingView.as_view(), name="recipe-rate"),
    path("recipes/<int:recipe_id>/ratings/", RecipeRatingListView.as_view(), name="recipe-ratings"),
    path("recipes/<int:recipe_id>/comments/", RecipeCommentListCreateView.as_view(), name="recipe-comments"),
    path("comments/<int:pk>/", CommentDetailView.as_view(), name="comment-detail"),
    path("saved/", SavedRecipeListView.as_view(), name="saved-list"),
    path("recipes/<int:recipe_id>/save/", RecipeSaveToggleView.as_view(), name="recipe-save"),
    path("recipes/<int:recipe_id>/share/", RecipeShareView.as_view(), name="recipe-share"),
]