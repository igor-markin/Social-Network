from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import Comment, Post
from posts.models import Group, User


class TestCommentForm(TestCase):
    def setUp(self):
        self.user_harry = User.objects.create_user(username='Harry')
        self.user_harry_client = Client()
        self.user_harry_client.force_login(self.user_harry)
        self.test_post = Post.objects.create(
            text='Test post',
            author=self.user_harry,
        )

    def test_add_comment(self):
        """Форма добавляет комментарий и редиректит обратно на пост."""
        comments_count = Comment.objects.count()
        form_data = {'text': 'Очень смешной комментарий', }
        args = [self.user_harry.username, self.test_post.id]
        response = self.user_harry_client.post(
            reverse('add_comment', args=args),
            data=form_data,
            follow=True)

        expected = comments_count + 1
        msg = 'Форма не добавляет новый комментарий'
        self.assertEqual(Post.objects.count(), expected, msg)

        expected = reverse('post', args=args)
        msg = 'Форма после добавления комментария не редиректит на пост'
        self.assertRedirects(response, expected, msg_prefix=msg)


class TestPostForm(TestCase):
    def setUp(self):
        self.user_igor = User.objects.create_user(username='Igor')
        self.user_igor_client = Client()
        self.user_igor_client.force_login(self.user_igor)

        self.test_post = Post.objects.create(
            text='Очень интересная заметка',
            author=self.user_igor,
        )
        self.test_group = Group.objects.create(
            title='Интересная группа для интересных людей',
            slug='super-duper-group',
        )

    def test_add_new_post(self):
        """Форма добавляет новый пост и редиректит на главную страницу."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Пост с полезной информацией', }
        response = self.user_igor_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True)

        expected = posts_count + 1
        msg = 'Форма не добавляет новый пост'
        self.assertEqual(Post.objects.count(), expected, msg)

        expected = reverse('index')
        msg = 'Форма после добавления поста не редиректит на главную'
        self.assertRedirects(response, expected, msg_prefix=msg)

    def test_add_new_post_with_group(self):
        """Форма добавляет пост с группой и редиректит на главную страницу."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Пост с полезной информацией',
            'group': self.test_group.id,
        }
        response = self.user_igor_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True)

        expected = posts_count + 1
        msg = 'Форма не добавляет новый пост с группой'
        self.assertEqual(Post.objects.count(), expected, msg)

        expected = reverse('index')
        msg = 'Форма после добавления поста с группой не редиректит на главную'
        self.assertRedirects(response, expected, msg_prefix=msg)

    def test_add_new_post_with_image(self):
        """Форма добавляет пост с фото и редиректит на главную страницу."""
        posts_count = Post.objects.count()
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B')
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        form_data = {
            'text': 'Пост с полезной информацией',
            'image': uploaded,
        }
        response = self.user_igor_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True)

        expected = posts_count + 1
        msg = 'Форма не добавляет новый пост с фото'
        self.assertEqual(Post.objects.count(), expected, msg)

        expected = reverse('index')
        msg = 'Форма после добавления поста с фото не редиректит на главную'
        self.assertRedirects(response, expected, msg_prefix=msg)

    def test_edit_post(self):
        """Форма редактирует пост и редиректит на страницу поста."""
        form_data = {'text': 'Более полезная информация, чем раньше', }
        response = self.user_igor_client.post(
            reverse('post_edit', args=[self.user_igor, self.test_post.id]),
            data=form_data,
            follow=True)

        self.test_post.refresh_from_db()
        msg = 'Форма не редактирует пост'
        self.assertEqual(self.test_post.text, form_data['text'], msg)

        expected = reverse('post', args=[self.user_igor, self.test_post.id])
        msg = 'Форма редактирования поста не редиректит на главную'
        self.assertRedirects(response, expected, msg_prefix=msg)

    def test_edit_post_with_group(self):
        """Форма редактирует пост с группой и редиректит на страницу поста."""
        form_data = {
            'text': 'Более полезная информация, чем раньше',
            'group': '',
        }
        response = self.user_igor_client.post(
            reverse('post_edit', args=[self.user_igor, self.test_post.id]),
            data=form_data,
            follow=True)

        self.test_post.refresh_from_db()
        msg = 'Форма не редактирует пост с группой'
        self.assertEqual(self.test_post.text, form_data['text'], msg)

        expected = reverse('post', args=[self.user_igor, self.test_post.id])
        msg = 'Форма редактирования поста с группой не редиректит на главную'
        self.assertRedirects(response, expected, msg_prefix=msg)

    def test_edit_post_with_image(self):
        """Форма редактирует пост с фото и редиректит на страницу поста."""
        form_data = {
            'text': 'Более полезная информация, чем раньше',
            'image': '',
        }
        response = self.user_igor_client.post(
            reverse('post_edit', args=[self.user_igor, self.test_post.id]),
            data=form_data,
            follow=True)

        self.test_post.refresh_from_db()
        msg = 'Форма не редактирует пост с фото'
        self.assertEqual(self.test_post.text, form_data['text'], msg)

        expected = reverse('post', args=[self.user_igor, self.test_post.id])
        msg = 'Форма редактирования поста с фото не редиректит на главную'
        self.assertRedirects(response, expected, msg_prefix=msg)
