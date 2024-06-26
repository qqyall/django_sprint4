from core.models import CreatedAtModel, PublishedModel
from django.contrib.auth import get_user_model
from django.db import models

from .consts import STR_MAX_LENGTH

User = get_user_model()


class Category(PublishedModel, CreatedAtModel):
    title = models.CharField(
        max_length=STR_MAX_LENGTH,
        verbose_name="Заголовок"
    )
    description = models.TextField(
        verbose_name="Описание"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
        help_text=("Идентификатор страницы для URL; "
                   "разрешены символы латиницы, цифры, дефис и подчёркивание.")
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return (self.title[:20] + '...' if len(self.title) > 20
                else self.title)


class Location(PublishedModel, CreatedAtModel):
    name = models.CharField(
        max_length=STR_MAX_LENGTH,
        verbose_name="Название места"
    )

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name


class Post(PublishedModel, CreatedAtModel):
    title = models.CharField(
        max_length=STR_MAX_LENGTH,
        verbose_name="Заголовок"
    )
    text = models.TextField(
        verbose_name="Текст"
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text=("Если установить дату и время в будущем "
                   "— можно делать отложенные публикации.")
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор публикации",
        on_delete=models.CASCADE,
    )
    location = models.ForeignKey(
        Location,
        verbose_name="Местоположение",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        on_delete=models.SET_NULL,
        null=True
    )
    image = models.ImageField(
        verbose_name='Фото',
        upload_to='posts_images',
        blank=True
    )

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ('-pub_date',)
        default_related_name = 'posts'

    def __str__(self):
        return self.title


class Comment(PublishedModel, CreatedAtModel):
    text = models.TextField(
        verbose_name="Комментарий"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ('created_at',)

    def __str__(self):
        return (
            f'post_id: {self.post}',
            f'user_id: {self.author}',
            f'text: {self.text}'
        )
