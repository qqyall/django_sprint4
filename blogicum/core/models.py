from django.db import models


class PublishedModel(models.Model):
    """Абстрактная модель. Добвляет флаг is_published."""

    is_published = models.BooleanField(
        default=True,
        help_text="Снимите галочку, чтобы скрыть публикацию.",
        verbose_name="Опубликовано"
    )

    class Meta:
        abstract = True


class CreatedAtModel(models.Model):
    """Абстрактная модель. Добвляет флаг created_at."""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=("Добавлено")
    )

    class Meta:
        abstract = True
