from django.core.validators import RegexValidator
from django.db.models import Avg
from rest_framework import serializers
from .models import Category, Product, Review


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z0-9-]+$",
                message="Slug должен состоять только из латинских букв, цифр и дефисов."
            )
        ]
    )

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "created_at"]
        read_only_fields = ["id", "created_at"]

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    owner = serializers.ReadOnlyField(source="owner.username")
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "category_name",
            "owner",
            "name",
            "description",
            "price",
            "in_stock",
            "created_at",
            "updated_at",
            "average_rating",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "owner", "category_name, average_rating"]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть больше нуля.")
        return value

    def validate_in_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Остаток на складе не может быть отрицательным.")
        return value

    def validate(self, attrs):
        name = attrs.get("name")
        if name and len(name) < 2:
            raise serializers.ValidationError(
                {"name": "Название товара должно быть не короче 2 символов."}
            )
        return attrs

    def get_average_rating(self, obj) -> float | None:
        average = getattr(obj, "average_rating", None)

        if average is None:
            average = Review.objects.filter(product=obj).aggregate(
                average=Avg("rating")
            )["average"]

        return float(average) if average is not None else None


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Review
        fields = ["id", "product", "user", "rating", "comment", "created_at"]
        read_only_fields = ["id", "user", "created_at"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Оценка должна быть от 1 до 5.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        product = attrs.get("product")

        if request and request.user.is_authenticated and product:
            if Review.objects.filter(product=product, user=request.user).exists():
                raise serializers.ValidationError(
                    {"product": "Вы уже оставили отзыв на этот товар."}
                )

        return attrs


class ProductDetailSerializer(ProductSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ["reviews"]


class CategoryDetailSerializer(CategorySerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + ["products"]
