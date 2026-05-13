from django.urls import path

from .views import (
    CuisineListView,
    MealTypeListView,
    RecipeDetailView,
    RecipeListCreateView,
    TagListView,
    UserRecipeListView,
)

urlpatterns = [
    path("", RecipeListCreateView.as_view(), name="recipe-list"),
    path("tags/", TagListView.as_view(), name="tag-list"),
    path("meal-types/", MealTypeListView.as_view(), name="meal-type-list"),
    path("cuisines/", CuisineListView.as_view(), name="cuisine-list"),
    path("by/<str:username>/", UserRecipeListView.as_view(), name="user-recipe-list"),
    path("<int:pk>/", RecipeDetailView.as_view(), name="recipe-detail"),
]