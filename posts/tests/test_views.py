import os
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User


class TemplatesTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(f'{settings.BASE_DIR}/tmp/', ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        os.mkdir(f'{settings.BASE_DIR}/tmp/')
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=f'{settings.BASE_DIR}/tmp/')

    def setUp(self):
        self.guest_client = Client()

        self.user_igor = User.objects.create_user(username='Igor')
        self.user_igor_client = Client()
        self.user_igor_client.force_login(self.user_igor)

        self.user_olga = User.objects.create_user(username='Olga')
        self.user_olga_client = Client()
        self.user_olga_client.force_login(self.user_olga)

        self.test_group = Group.objects.create(
            title='Test Group',
            slug='group',
            description='Description',
        )

        self.test_second_group = Group.objects.create(
            title='Test Second Group',
            slug='second-group',
            description='Description',
        )

        self.small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                          b'\x01\x00\x80\x00\x00\x00\x00\x00'
                          b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                          b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                          b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                          b'\x0A\x00\x3B')

        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif',
        )

        self.test_post = Post.objects.create(
            text='Test post',
            author=self.user_igor,
            group=self.test_group,
            image=self.uploaded,
        )

    def test_auth_user_can_follow_unfollow(self):
        """Пользователь может подписаться и отписаться от автора."""
        urls = {
            reverse('profile_follow', args=[self.user_olga]): True,
            reverse('profile_unfollow', args=[self.user_olga]): False,
        }

        for url, expected in urls.items():
            with self.subTest(url=url):
                self.user_igor_client.get(url)
                actual = Follow.objects.filter(
                    user=self.user_igor,
                    author=self.user_olga
                ).exists()
                msg = f'{url}: подписка/отписка работает неправильно'
                self.assertEqual(actual, expected, msg)

    def test_new_post_exist_for_followers(self):
        test_post_olga = Post.objects.create(
            text='Test Olga post',
            author=self.user_olga,
            group=self.test_group,
        )

        follow = reverse('profile_follow', args=[self.user_olga])
        self.user_igor_client.get(follow)

        url = reverse('follow_index')

        response = self.user_igor_client.get(url)
        actual = response.context['page'][0]
        expected = test_post_olga

        msg = 'Неправильно работает страница избранного.'

        self.assertEqual(actual, expected, msg)

        response = self.user_olga_client.get(url)
        actual = response.context['paginator'].count

        self.assertEqual(actual, 0, msg)

    def test_auth_user_can_comment(self):
        """Пользователи могут добавлять комментарии, а гости нет."""
        users = {
            self.guest_client: False,
            self.user_igor_client: True,
        }

        for user, expected in users.items():
            with self.subTest(user=user):
                form_data = {
                    'text': 'My comment',
                }

                user.post(
                    reverse('add_comment',
                            args=[self.user_igor, self.test_post.id]),
                    data=form_data,
                    follow=True,
                )

                actual = Comment.objects.filter(
                    post=self.test_post,
                    author=self.user_igor,
                    text=form_data['text'],
                ).exists()

                msg = f'Ошибка добавления комментария у {user}'

                self.assertEqual(actual, expected, msg)

    def test_cache(self):
        """Главная страница корректно кэширует список записей."""
        first_response = self.guest_client.get(reverse('index'))
        first_post = first_response.context['page'][0]

        self.test_post.text = 'Surprise'

        second_response = self.guest_client.get(reverse('index'))
        second_post = second_response.context['page'][0]

        msg = 'На главной странице не работает кэширование'

        self.assertEqual(first_post, second_post, msg)

    def test_url_templates(self):
        """Вызываемые шаблоны соответствуют задуманному."""
        user = self.user_igor
        post_id = self.test_post.id
        urls = {
            reverse('index'): 'index.html',
            reverse('new_post'): 'new_post.html',
            reverse('group', args=['group']): 'group.html',
            reverse('group', args=['group']): 'group.html',
            reverse('post_edit', args=[user, post_id]): 'new_post.html',
            reverse('about_author'): 'about/author.html',
            reverse('about_tech'): 'about/tech.html',
        }

        for url, expected in urls.items():
            with self.subTest():
                response = self.user_igor_client.get(url)
                msg = f'{url} не использует шаблон {expected}'
                self.assertTemplateUsed(response, expected, msg)

    def test_index_context(self):
        """На главной странице существует пост и правильный контекст."""
        response = self.user_igor_client.get(reverse('index'))
        expected = self.test_post
        msg = 'На главной странице неправильный context или нет нового поста'
        self.assertEqual(response.context['page'][0], expected, msg)

    def test_group_context(self):
        """На странице группы правильный контекст."""
        url = reverse('group', args=['group'])
        response = self.user_igor_client.get(url)
        expected = self.test_group
        msg = 'На странице группы неправильный context'
        self.assertEqual(response.context['group'], expected, msg)

    def test_new_post_context(self):
        """На странице создания поста правильный контекст."""
        fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }

        response = self.user_igor_client.get(reverse('new_post'))
        form = response.context['form']

        for field, expected in fields.items():
            with self.subTest(field=field):
                msg = 'На странице создания поста неправильный context'
                self.assertIsInstance(form.fields[field], expected, msg)

    def test_post_edit_context(self):
        """На странице редактирования поста правильный контекст."""
        url = reverse('post_edit', args=[self.user_igor, self.test_post.id])
        response = self.user_igor_client.get(url)
        form = response.context['form']

        context = {
            'post': self.test_post,
            'is_edit': True,
        }

        for value, expected in context.items():
            with self.subTest(value=value):
                msg = f'{value} контекста не равно {expected}'
                self.assertEqual(response.context[value], expected, msg)

        fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for field, expected in fields.items():
            with self.subTest(field=field):
                msg = 'На странице редактирования поста неправильный context'
                self.assertIsInstance(form.fields[field], expected, msg)

    def test_profile_context(self):
        """На странице автора правильный контекст."""
        user = self.user_igor
        url = reverse('profile', args=[user])
        response = self.user_igor_client.get(url)

        context = {
            'author': user,
            'post': self.test_post,
        }

        for value, expected in context.items():
            with self.subTest(value=value):
                msg = f'{value} контекста не равно {expected}'
                self.assertEqual(response.context[value], expected, msg)

    def test_post_view_context(self):
        """На странице поста правильный контекст."""
        url = reverse('post', args=[self.user_igor, self.test_post.id])
        response = self.user_igor_client.get(url)

        context = {
            'post': self.test_post,
            'author': self.user_igor,
        }

        for value, expected in context.items():
            with self.subTest(value=value):
                msg = f'{value} контекста не равно {expected}'
                self.assertEqual(response.context[value], expected, msg)

    def test_group_post(self):
        """На странице группы отображается новый пост."""
        response = self.user_igor_client.get(
            reverse('group', args=['group']))
        expected = self.test_post
        msg = 'На странице группы не отображается новый пост'
        self.assertEqual(response.context['page'][0], expected, msg)

    def test_another_group_post(self):
        """На странице другой группы не отображается новый пост."""
        path = reverse('group', args=['second-group'])
        response = self.user_igor_client.get(path)
        response = response.context['page'].object_list.count()
        expected = 0
        msg = 'На странице другой группы не должен отображаться новый пост'
        self.assertEqual(response, expected, msg)


class PaginatorViewTest(TestCase):
    def setUp(self):
        self.user_igor = User.objects.create_user(username='Igor')
        self.user_igor_client = Client()
        self.user_igor_client.force_login(self.user_igor)

        self.test_group = Group.objects.create(
            title='Test Group',
            slug='group',
            description='Description',
        )

        for _ in range(15):
            Post.objects.create(
                text='Test post',
                author=self.user_igor,
                group=self.test_group,
            )

    def test_first_page(self):
        """На первой странице пагинатор нужное количество постов."""
        slug = self.test_group.slug

        pages = (
            reverse('index'),
            reverse('group', args=[slug])
        )

        for page in pages:
            with self.subTest(page=page):
                response = self.user_igor_client.get(page)
                response = len(response.context['page'].object_list)
                expected = settings.POSTS_PER_PAGE
                msg = f'На странице {page} не {expected} сообщений'
                self.assertEqual(response, expected, msg)

    def test_second_page(self):
        """На второй странице пагинатор нужное количество постов."""
        slug = self.test_group.slug

        pages = (
            reverse('index'),
            reverse('group', args=[slug])
        )

        for page in pages:
            with self.subTest(page=page):
                response = self.user_igor_client.get(page + '?page=2')
                response = len(response.context['page'].object_list)
                expected = 5
                msg = f'На второй странице не {expected} сообщений'
                self.assertEqual(response, expected, msg)
