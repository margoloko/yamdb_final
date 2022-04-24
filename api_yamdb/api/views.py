from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

from rest_framework import viewsets, status, filters, mixins
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb.settings import PROJECT_MAIL

from .serializers import (
    UserSerializer, UserAuthSerializer, UserTokenSerializer,
    CommentSerializer, ReviewSerializer, GenreSerializer,
    TitleSerializer, CategorySerializer, TitleReadSerializer
)
from .permissions import (AdminRoleOnly, ReadOnly,
                          IsAuthorModeratorAdminOrReadOnly)
from reviews.models import Genre, Title, Category, Review
from api.filters import TitleFilter


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Класс-вьюсет для модели User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminRoleOnly,)
    lookup_field = 'username'
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('username',)


class PersonalUserViewSet(viewsets.ViewSet):
    """Класс-вьюсет модели User для получения
    персональной информации учетной записи."""

    def retrieve(self, request, pk=None):
        """Функция для получения данных по своей учетной записи."""
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        """Функция для обновления данных своей учетной записи."""
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # Обработка попытки изменения роли обычным юзером
        if user.role != User.USER:
            serializer.save()
        else:
            serializer.save(role=user.role)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """View-функция для регистрации новых пользователей."""
    serializer = UserAuthSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = get_object_or_404(
            User, username=serializer.validated_data['username']
        )
        token = default_token_generator.make_token(user)
        send_mail(
            'Код подтверждения',
            'Ваш код подтверждения: <{}>'.format(token),
            PROJECT_MAIL,
            [serializer.validated_data['email']],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_emission(request):
    """View-функция для выдачи токена пользователю."""
    serializer = UserTokenSerializer(data=request.data)
    if serializer.is_valid():
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username']
        )
        refresh = RefreshToken.for_user(user)
        return Response(
            {'token': str(refresh.access_token)}, status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListCreateDeleteViewSet(mixins.DestroyModelMixin,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              viewsets.GenericViewSet):
    pass


class CategoryViewSet(ListCreateDeleteViewSet):
    """View-функция для категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminRoleOnly | ReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']
    lookup_field = 'slug'


class GenreViewSet(ListCreateDeleteViewSet):
    """View-функция для жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AdminRoleOnly | ReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """View-функция для произведений."""
    queryset = Title.objects.all()
    permission_classes = [AdminRoleOnly | ReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """View-функция для отзывов на произведения."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorModeratorAdminOrReadOnly, ]

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        if Review.objects.filter(
            author=self.request.user, title=self.get_title()
        ):
            raise ValidationError('Ваш отзыв на это произведение уже есть')
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """View-функция для комментариев на отзывы."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorModeratorAdminOrReadOnly, ]

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )
