from rest_framework.test import APITestCase
from likenpost.apps.post.factories import UserFactory, PostFactory
from rest_framework.reverse import reverse
from likenpost.apps.post.models import Post, Like


class LikeApiTestCase(APITestCase):

    def like_url(self, pk):
        return self.url + '%d/like/' % pk

    def unlike_url(self, pk):
        return self.url + '%d/unlike/' % pk

    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('post:post')
        self.post = PostFactory(owner=self.user)

    def test__like(self):

        response = self.client.post(
            self.like_url(self.post.pk)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'OK')
        self.assertEqual(Like.objects.filter(post=self.post, owner=self.user).count(), 1)

    def test__like_unlike(self):

        response = self.client.post(
            self.like_url(self.post.pk)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'OK')
        self.assertEqual(Like.objects.filter(post=self.post, owner=self.user).count(), 1)

        response = self.client.post(
            self.unlike_url(self.post.pk)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'OK')
        self.assertEqual(Like.objects.filter(post=self.post, owner=self.user).count(), 0)

    def test__like_like(self):

        response = self.client.post(
            self.like_url(self.post.pk)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'OK')
        self.assertEqual(Like.objects.filter(post=self.post, owner=self.user).count(), 1)

        response = self.client.post(
            self.like_url(self.post.pk)
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, 'Already liked')
        self.assertEqual(Like.objects.filter(post=self.post, owner=self.user).count(), 1)

    def test__unlike(self):

        self.assertEqual(Like.objects.filter(post=self.post, owner=self.user).count(), 0)
        response = self.client.post(
            self.unlike_url(self.post.pk)
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, 'You have to like the post first.')
        self.assertEqual(Like.objects.filter(post=self.post, owner=self.user).count(), 0)

    def test__delete_likes_when_deleting_post(self):

        post = PostFactory(owner=self.user)
        response = self.client.post(
            self.like_url(post.pk)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Like.objects.filter(post=post, owner=self.user).count(), 1)

        response = self.client.delete(
            self.url + str(post.pk) + '/'
        )

        self.assertEqual(response.status_code, 204)

        # There should be no likes

        self.assertEqual(Like.objects.filter(post=post, owner=self.user).count(), 0)
