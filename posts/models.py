from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
        help_text='Укажите название группы',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Ссылка',
        help_text='Укажите короткую ссылку',
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Коротко опишите вашу группу',
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст заметки',
        help_text='Напишите то, что хотели написать',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Укажите имя автора',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу для публикации',
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        verbose_name='Изображение',
        help_text='Выберите файл изображения',
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост для комментирования',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Напишите, что вы думаете о теме',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания комментария',
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь, который подписывается',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Пользователь, на которого подписываются',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author',],
                name = 'unique_follows',
            )
        ]
