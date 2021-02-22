from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image',)
        labels = {
            'group': 'Название группы',
            'text': 'Текст заметки',
            'image': 'Изображение',
        }
        help_texts = {
            'group': 'Укажите название группы',
            'text': 'Напишите то, что хотели написать',
            'image': 'Выберите файл изображения',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Комментарий',
        }
        help_texts = {
            'text': 'Напишите, что вы думаете о теме',
        }
