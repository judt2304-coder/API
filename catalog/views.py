from django.db.models import Avg, Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .filters import ProductFilter
from .models import Category, Product, Review
from .permissions import IsOwnerOrReadOnly, IsReviewAuthorOrReadOnly
from .serializers import (
    CategoryDetailSerializer,
    CategorySerializer,
    ProductDetailSerializer,
    ProductSerializer,
    ReviewSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="Список категорий", tags=["Категории"]),
    retrieve=extend_schema(summary="Получить категорию", tags=["Категории"]),
    create=extend_schema(summary="Создать категорию", tags=["Категории"]),
    update=extend_schema(summary="Полностью обновить категорию", tags=["Категории"]),
    partial_update=extend_schema(summary="Частично обновить категорию", tags=["Категории"]),
    destroy=extend_schema(summary="Удалить категорию", tags=["Категории"]),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                Prefetch(
                    "products",
                    queryset=Product.objects.select_related("category", "owner")
                )
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CategoryDetailSerializer
        return CategorySerializer


@extend_schema_view(
    list=extend_schema(summary="Список товаров", tags=["Товары"]),
    retrieve=extend_schema(summary="Получить товар", tags=["Товары"]),
    create=extend_schema(summary="Создать товар", tags=["Товары"]),
    update=extend_schema(summary="Полностью обновить товар", tags=["Товары"]),
    partial_update=extend_schema(summary="Частично обновить товар", tags=["Товары"]),
    destroy=extend_schema(summary="Удалить товар", tags=["Товары"]),
)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category", "owner").all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at", "in_stock"]

    def get_queryset(self):
        queryset = (
            self.queryset
            .annotate(average_rating=Avg("reviews__rating"))
            .order_by("-created_at")
        )

        if self.action == "retrieve":
            queryset = queryset.prefetch_related("reviews__user")

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@extend_schema_view(
    list=extend_schema(summary="Список отзывов", tags=["Отзывы"]),
    retrieve=extend_schema(summary="Получить отзыв", tags=["Отзывы"]),
    create=extend_schema(summary="Создать отзыв", tags=["Отзывы"]),
    update=extend_schema(summary="Полностью обновить отзыв", tags=["Отзывы"]),
    partial_update=extend_schema(summary="Частично обновить отзыв", tags=["Отзывы"]),
    destroy=extend_schema(summary="Удалить отзыв", tags=["Отзывы"]),
)
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.select_related("product", "user").all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsReviewAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["product"]
    ordering_fields = ["rating", "created_at"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
