from django.db.models import Q
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import RecipeFilter
from .models import MealType, Recipe, Tag
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    MealTypeSerializer,
    RecipeDetailSerializer,
    RecipeListSerializer,
    TagSerializer,
)

User = get_user_model()


# ─── Tag & MealType ────────────────────────────────────────────────────────────

class TagListView(generics.ListCreateAPIView):
    """GET /api/v1/recipes/tags/ — list all tags (authenticated to create)."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MealTypeListView(generics.ListCreateAPIView):
    """GET /api/v1/recipes/meal-types/"""

    queryset = MealType.objects.all()
    serializer_class = MealTypeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ─── Recipe CRUD ───────────────────────────────────────────────────────────────

class RecipeListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/recipes/         — paginated, filterable recipe list.
    POST /api/v1/recipes/         — create a new recipe (auth required).

    Query params:
        search=<term>             full-text across name, cuisine, ingredients
        cuisine=Italian
        difficulty=Easy|Medium|Hard
        min_calories / max_calories
        max_time=<minutes>
        meal_type=Dinner
        tag=Pasta
        min_rating=4
        author=<username>
        ordering=rating|-created_at|cook_time_minutes
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_class = RecipeFilter
    search_fields = ["name", "description", "cuisine", "tags__name", "meal_types__name"]
    ordering_fields = ["rating", "created_at", "prep_time_minutes", "cook_time_minutes", "calories_per_serving"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Recipe.objects.filter(is_published=True)
            .select_related("author")
            .prefetch_related("tags", "meal_types")
            .distinct()
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RecipeDetailSerializer
        return RecipeListSerializer

    def perform_create(self, serializer):
        recipe = serializer.save(author=self.request.user)
        # Update author's recipe counter
        User.objects.filter(pk=self.request.user.pk).update(
            recipes_count=self.request.user.recipes_count + 1
        )
        return recipe


class RecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PUT / PATCH / DELETE /api/v1/recipes/<id>/"""

    serializer_class = RecipeDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        return (
            Recipe.objects.select_related("author")
            .prefetch_related("tags", "meal_types")
        )

    def perform_destroy(self, instance):
        author = instance.author
        instance.delete()
        User.objects.filter(pk=author.pk).update(
            recipes_count=max(0, author.recipes_count - 1)
        )


# ─── User recipe list ──────────────────────────────────────────────────────────

class UserRecipeListView(generics.ListAPIView):
    """GET /api/v1/recipes/by/<username>/ — all published recipes by a user."""

    serializer_class = RecipeListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Recipe.objects.none()
        user = get_object_or_404(User, username=self.kwargs["username"])
        return (
            Recipe.objects.filter(author=user, is_published=True)
            .select_related("author")
            .prefetch_related("tags", "meal_types")
        )


# ─── Cuisine & Tag exploration ─────────────────────────────────────────────────

@extend_schema(
    responses={200: {"type": "array", "items": {"type": "string"}, "example": ["Italian", "Mexican", "Indian"]}},
    description="Return a sorted list of all distinct cuisine values from published recipes.",
)
class CuisineListView(APIView):
    """GET /api/v1/recipes/cuisines/ — distinct cuisine values."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cuisines = (
            Recipe.objects.filter(is_published=True)
            .exclude(cuisine="")
            .values_list("cuisine", flat=True)
            .distinct()
            .order_by("cuisine")
        )
        return Response(list(cuisines))