from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class URLTests(TestCase):
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

        self.test_post = Post.objects.create(
            text='Test post',
            author=self.user_igor,
            group=self.test_group,
        )

    def test_urls_allowed_for_guests(self):
        """Ссылки, которые может открывать гость."""
        urls = [
            reverse('index'),
            reverse('about_tech'),
            reverse('about_author'),
            reverse('group', args=['group']),
            reverse('profile', args=[self.user_igor]),
            reverse('post', args=[self.user_igor, self.test_post.id]),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                msg = f'У гостя не открывается страница {url}'
                self.assertEqual(response.status_code, 200, msg)

    def test_urls_forbidden_for_guests(self):
        """Ссылки, по которым гость ходить не может: работает редирект."""
        urls = [
            reverse('new_post'),
            reverse('post_edit', args=[self.user_igor, self.test_post.id]),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                expected = f'/auth/login/?next={url}'
                msg = f'У гостя не должна открываться страница {url}'
                self.assertRedirects(response, expected, msg_prefix=msg)

    def test_urls_allowed_for_users(self):
        """Ссылки, которые должны открываться у авторизованного юзера."""
        urls = [
            reverse('new_post'),
            reverse('post_edit', args=[self.user_igor, self.test_post.id]),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.user_igor_client.get(url)
                msg = f'Пользователь не может открыть страницу {url}'
                self.assertEqual(response.status_code, 200, msg)

    def test_url_forbidden_for_another_users(self):
        """Ссылка, с которых людей, не создававших пост, будет редиректить."""
        url = reverse('post_edit', args=[self.user_igor, self.test_post.id])
        response = self.user_olga_client.get(url, follow=True)
        expected = reverse('post', args=[self.user_igor, self.test_post.id])
        msg = f'Только у автора должна открываться страница {url}'
        self.assertRedirects(response, expected, msg_prefix=msg)

    def test_404_not_found(self):
        """Сервер возвращает код 404 на запрос несуществующей страницы."""
        response = self.guest_client.get('/ingvar/')
        msg = 'Сервер не возвращает код 404 на запрос несуществующей страницы'
        self.assertEqual(response.status_code, 404, msg)
