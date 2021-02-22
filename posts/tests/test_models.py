from django.test import Client, TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Igor')
        self.user_client = Client()
        self.user_client.force_login(self.user)

        self.test_post = Post.objects.create(
            text='F' * 20,
            author=self.user,
        )

    def test_verbose_name(self):
        names = {
            'text': 'Текст заметки',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }

        post = self.test_post

        for value, expected in names.items():
            with self.subTest(value=value):
                actual = post._meta.get_field(value).verbose_name
                msg = f'У поля {value} не должен меняться verbose_name'
                self.assertEqual(actual, expected, msg)

    def test_help_text(self):
        texts = {
            'text': 'Напишите то, что хотели написать',
            'author': 'Укажите имя автора',
            'group': 'Выберите группу для публикации',
        }

        for value, expected in texts.items():
            with self.subTest(value=value):
                actual = self.test_post._meta.get_field(value).help_text
                msg = f'У поля {value} не должен меняться help_text'
                self.assertEqual(actual, expected, msg)

    def test_group_str(self):
        test_group = Group.objects.create(
            title='Test Group',
            slug='group',
            description='Description',
        )

        actual = str(test_group)
        expected = test_group.title
        msg = '__str__ группы не совпадает с заголовком'
        self.assertEqual(actual, expected, msg)

    def test_post_str(self):
        actual = str(self.test_post)
        msg = '__str__ поста не обрезается до нужного количества символов'
        self.assertEqual(actual, actual[:15], msg)
