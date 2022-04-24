from django.db.models import Avg
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import Comment, Review, Genre, Title, Category


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Класс для сериализации модели User."""

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User


class UserAuthSerializer(serializers.ModelSerializer):
    """Класс для сериализации модели User при регистрации."""

    class Meta:
        fields = ('username', 'email')
        model = User

    def validate_username(self, value):
        """Функция-валидатор для поля username."""

        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя регистрировать пользователя с именем "me"!'
            )
        return value


class UserTokenSerializer(serializers.Serializer):
    """Класс для сериализации модели User при выдаче JWT токена."""
    confirmation_code = serializers.CharField()
    username = serializers.CharField(max_length=150)

    def validate(self, attrs):
        """Валидация входных данных при выдаче токена."""
        user = get_object_or_404(User, username=attrs['username'])
        if not default_token_generator.check_token(user,
                                                   attrs['confirmation_code']):

            raise serializers.ValidationError(
                'Ваш токен невалидный или устарел!'
            )
        return attrs


class CategorySerializer(serializers.ModelSerializer):
    """Класс для сериализации категорий."""
    slug = serializers.SlugField(validators=[UniqueValidator(
        queryset=Category.objects.all())])

    class Meta:
        exclude = ['id']
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Класс для сериализации жанров."""
    slug = serializers.SlugField(validators=[UniqueValidator(
        queryset=Genre.objects.all())])

    class Meta:
        exclude = ['id']
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    """Класс для сериализации тайтлов."""
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug')
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), many=True, slug_field='slug')

    class Meta:
        fields = '__all__'
        model = Title


class TitleReadSerializer(serializers.ModelSerializer):
    """Класс для сериализации тайтлов."""
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Title

    def get_rating(self, obj):
        average_score_dict = Review.objects.filter(
            title=obj).aggregate(Avg('score'))
        average_score = average_score_dict.get('score__avg')
        if average_score:
            return round(average_score)


class CommentSerializer(serializers.ModelSerializer):
    """Класс для сериализации комментариев."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('author', 'pub_date')
        model = Comment
        ordering = ['-id']


class ReviewSerializer(serializers.ModelSerializer):
    """Класс для сериализации отзывов на произведения."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')
    score = serializers.IntegerField(max_value=10, min_value=1)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('author', 'pub_date')
        model = Review
        ordering = ['-id']
