from rest_framework.test import APITestCase
from likenpost.apps.post.factories import UserFactory, PostFactory
from rest_framework.reverse import reverse
from likenpost.apps.post.models import Post, Like


class PostApiTestCase(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('post:post')

    def test__create(self):

        response = self.client.post(
            self.url,
            data={'content': 'content'}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['owner'], self.user.username)

    def test__get(self):
        test_content = 'test content'
        post = PostFactory(owner=self.user, content=test_content)

        response = self.client.get(
            self.url + str(post.pk) + '/',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['owner'], self.user.username)
        self.assertEqual(response.data['content'], test_content)

    def test__get_3_posts(self):
        users = [self.user, UserFactory(), UserFactory()]
        PostFactory(owner=users[0])
        PostFactory(owner=users[1])
        PostFactory(owner=users[2])

        usernames = [x.username for x in users]

        response = self.client.get(
            self.url,
        )
        self.assertEqual(response.status_code, 200)
        for post in response.data:
            self.assertTrue(post['owner'] in usernames)

    def test__put(self):
        test_content = 'test content'
        new_content = 'new content'
        post = PostFactory(owner=self.user, content=test_content)

        response = self.client.put(
            self.url + str(post.pk) + '/',
            data={'content': new_content}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['owner'], self.user.username)
        self.assertEqual(response.data['content'], new_content)

    def test__delete(self):
        test_content = 'test content'
        post = PostFactory(owner=self.user, content=test_content)

        response = self.client.delete(
            self.url + str(post.pk) + '/',
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Post.objects.filter(owner=self.user, content=test_content).count(), 0)

    def test__put_rejected(self):
        user = UserFactory()
        test_content = 'test content'
        new_content = 'new content'
        post = PostFactory(owner=user, content=test_content)

        response = self.client.put(
            self.url + str(post.pk) + '/',
            data={'content': new_content}
        )
        self.assertEqual(response.status_code, 404)

    def test__delete_rejected(self):
        user = UserFactory()
        test_content = 'test content'
        post = PostFactory(owner=user, content=test_content)

        response = self.client.delete(
            self.url + str(post.pk) + '/',
        )
        self.assertEqual(response.status_code, 404)
