from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime as dt


CURRENT_YEAR = dt.datetime.now().year


class User(AbstractUser):
    """Кастомный класс для пользователей."""
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = [
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь'),
    ]

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=9, choices=ROLES, default=USER)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.username


class Category(models.Model):
    """Класс Categories определяет категории(типы) произведений."""
    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(max_length=50)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.slug


class Genre(models.Model):
    """Класс Geners описывает жанры произведений."""
    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.slug


class Title(models.Model):
    """Произведения, к которым пишут отзывы."""
    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    year = models.PositiveIntegerField(
        default=CURRENT_YEAR,
        help_text='год выпуска не может быть больше текущего'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория'
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'year', 'category'],
                name='unique_title'
            ),
            models.CheckConstraint(
                check=models.Q(year__gte=1500)
                & models.Q(year__lte=CURRENT_YEAR),
                name='1500_to_current_year'
            ),
        ]

    def __str__(self):
        return self.name


class Review(models.Model):
    """Класс описывает рецензии к произведениям."""
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        help_text='Укажите рейтинг от 1 до 10',
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            ),
            models.CheckConstraint(
                check=models.Q(score__gte=1) | models.Q(score__lte=10),
                name='1_to_10_score_range'
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Класс описывает комментарии к рецензиям."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'text', 'review'],
                name='unique_comment'
            )
        ]

    def __str__(self):
        return self.text
