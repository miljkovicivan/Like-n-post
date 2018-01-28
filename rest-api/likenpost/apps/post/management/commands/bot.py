import factory
import requests
import yaml
import json
import faker
import random
from django.core.management.base import BaseCommand
from likenpost.apps.post.factories import UserFactory
import asyncio
import aiohttp


class Command(BaseCommand):

    def get_url(self, url):
        return 'http://' + self.options['base_url'] + url + '?bot=True'

    def add_arguments(self, parser):
        parser.add_argument('base_url', type=str)
        parser.add_argument('--config', default='conf.yml', type=str, required=False)

    def handle(self, *args, **options):
        self.options = options

        self.semaphore = asyncio.Semaphore(10)
        with open('./bot_conf/' + self.options['config'], 'r') as f:
            self.config = yaml.load(f)

        asyncio.get_event_loop().run_until_complete(self.bot())

    def create_users(self):
        return [
            factory.build(
            dict,
            FACTORY_CLASS=UserFactory,
            user_additional_data=None
        ) for i in range(self.config['number_of_users'])]


    async def bot(self):
        users = self.create_users()

        users = await asyncio.gather(
            *[self.signup_user(user) for user in users]
        )

        users = await asyncio.gather(
            *[self.signin_user(user) for user in users]
        )

        posts = []
        for user in users:
            number_of_posts = random.randint(1, self.config['max_posts_per_user'])
            user['number_of_posts'] = number_of_posts

            posts += [self.create_post_for_user(user) for i in range(number_of_posts)]

        posts = await asyncio.gather(*posts)

        # users withe the most posts likes first
        users.sort(key=lambda x: -x['number_of_posts'])

        for user in users:

            await asyncio.gather(
                *[self.like(user, post) for post in self.find_posts_to_like(user, posts)]
            )

    async def like(self, user, post):
        with await self.semaphore:
            async with aiohttp.ClientSession() as session:
                url = post['url'] + 'like/'
                headers = {'Authorization': 'JWT ' + user['token']}
                async with session.post(url, headers=headers) as response:
                    data = await response.json()
                    assert response.status, 200

    def find_posts_to_like(self, user, posts):
        not_my_posts = [post for post in posts if post['owner'] != user['username'] and user['username'] not in post['likes']]

        random.shuffle(not_my_posts)

        num_of_posts = 0
        while(num_of_posts != self.config['max_likes_per_user'] and len(not_my_posts) != 0):
            post = not_my_posts.pop()
            if self.owner_has_zero_likes(post, posts):
                yield post
                post['likes'].append(user['username'])
                num_of_posts += 1

    def owner_has_zero_likes(self, post, posts):
        my_posts = [p for p in posts if post['owner'] == p['owner']]

        posts_with_zero_likes = [p for p in my_posts if len(p['likes']) == 0]

        if len(posts_with_zero_likes) == 0:
            return False
        else:
            return True

    async def signup_user(self, user):
        payload = {
            'username': user['username'],
            'password': user['password'],
            'email': user['email'],
        }
        with await self.semaphore:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.get_url('/api/user/'), data=payload) as response:
                    data = await response.json()
                    data['password'] = user['password'] # needed for login
                    assert response.status, 201
                    return data

    async def signin_user(self, user):
        payload = {
            'username': user['username'],
            'password': user['password']
        }
        with await self.semaphore:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.get_url('/api/login/'), data=payload) as response:
                    data = await response.json()
                    assert response.status, 200
                    user['token'] = data['token']
                    return user

    async def create_post_for_user(self, user):
        f = faker.Faker()
        payload = {'content': f.sentence()}
        with await self.semaphore:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.get_url('/api/post/'), data=payload, headers={'Authorization': 'JWT ' + user['token']}) as response:
                    data = await response.json()
                    assert response.status, 201
                    return data
