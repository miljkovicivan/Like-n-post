import factory
import requests
import yaml
import json
import faker
import random
from django.core.management.base import BaseCommand, CommandError
from likenpost.apps.post.models import Post, Like
from likenpost.apps.post.factories import UserFactory
from copy import deepcopy


class Command(BaseCommand):

    def get_url(self, url):
        return 'http://' + self.options['base_url'] + url + '?bot=True'

    def jsonify_response(self, response):
        return json.loads(response.content.decode('utf-8'))

    def add_arguments(self, parser):
        parser.add_argument('base_url', type=str)
        parser.add_argument('--config', default='conf.yml', type=str, required=False)

    def handle(self, *args, **options):
        self.options = options

        with open('./bot_conf/' + self.options['config'], 'r') as f:
            self.config = yaml.load(f)

        users = self.create_users()
        users = self.signup_users(users)
        users = self.signin_users(users)
        users = self.create_posts(users)

        users.sort(key=lambda x: x['number_of_posts'])

        self.let_the_liking_begin(users)

    def let_the_liking_begin(self, users):

        end = False
        while not end:

            user = self.next_user_to_like(users)
            if user is None:
                end = True
                break
            user = self.update_user(users, user)

            for i in range(self.config['max_likes_per_user']):

                post = self.find_post_to_like(user, users)
                if post and (user['username'] in post['likes'] or post['id'] in user['likes']):
                    '''
                    Somehow `find_post_to_like` returns already liked post
                    This is dirty fix to avoid this.
                    '''
                    #import pdb; pdb.set_trace()
                    i -= 1
                    continue

                if post is None:
                    if self.post_with_no_likes_exists(users, user):
                        break
                    else:
                        end = True
                        break

                self.like_post(post, user)
                users = self.update_users_list(users, post, user)
                user = self.update_user(users, user)


    def update_user(self, users, user):
        for u in users:
            if u['username'] == user['username']:
                return u

    def like_post(self, post, user):
        response = requests.post(
            post['url'] + 'like/',
            headers = {'Authorization': 'JWT ' + user['token']}
        )

        assert response.status_code, 200

    def find_user_by_id(self, pk, users):
        for u in users:
            if u['id'] == pk:
                return u

    def update_users_list(self, users, post, user):
        for u in users:
            if u['username'] == user['username']:
                u['likes'].append(post['id'])
            if u['username'] == post['owner']:
                for p in u['posts']:
                    if p['url'] == post['url']:
                        response = requests.get(
                            p['url'],
                            headers={'Authorization': 'JWT ' + user['token']}
                        )
                        assert response.status_code, 200
                        p['likes'] = self.jsonify_response(response)['likes']
        return users

    def post_with_no_likes_exists(self, users, user):
        for user in users:
            for post in user['posts']:
                '''
                Posible outcome: Last user have 1 post with no likes.
                He is the only one left so he enters infinity loop
                '''
                if len(post['likes']) == 0 and user['username'] != user['username']:
                    return True
        return False

    def find_post_to_like(self, user, users):

        all_posts = []
        for user in users:
            all_posts += user['posts']

        relevant_posts = []
        for p in all_posts:
            if p['owner'] != user['username'] and user['username'] not in p['likes'] and p['id'] not in user['likes']:
                relevant_posts.append(p)

        post = None
        end = False
        while not end:
            index = random.randint(0, len(relevant_posts) - 1)

            post = relevant_posts[index]
            if self.user_have_posts_with_zero_likes(post['owner'], users):
                end = True
                break
            else:
                relevant_posts.pop(index)

            if not relevant_posts:
                post = None
                end = True
                break

        if post and (user['username'] in post['likes'] or post['id'] in user['likes']):
            import pdb; pdb.set_trace()

        return post


    def user_have_posts_with_zero_likes(self, username, users):
        user_posts = [user['posts'] for user in users if user['username'] == username][0]
        for post in user_posts:
            if len(post['likes']) == 0:
                return True
        return False

    def next_user_to_like(self, users):
        for user in users:
            if len(user['likes']) != self.config['max_likes_per_user']:
                return user

    def create_posts_for_user(self, user):

        user['posts'] = []
        user['likes'] = []
        number_of_posts = random.randint(1, self.config['max_posts_per_user'])
        user['number_of_posts'] = number_of_posts
        f = faker.Faker()

        for i in range(number_of_posts):
            payload = {'content': f.sentence()}
            response = requests.post(
                self.get_url('/api/post/'),
                data=payload,
                headers = {'Authorization': 'JWT ' + user['token']}
            )
            assert response.status_code, 201
            data = self.jsonify_response(response)
            user['posts'].append(data)


        return user

    def create_posts(self, users):
        f = faker.Faker()
        for user in users:
            user = self.create_posts_for_user(user)

        return users

    def create_users(self):
        users = []
        for i in range(self.config['number_of_users']):
            users.append(
                factory.build(
                    dict,
                    FACTORY_CLASS=UserFactory,
                    user_additional_data=None
                )
            )
        return users

    def signup_users(self, users):
        prepared_user_data = map(lambda x:
                {
                    'username': x['username'],
                    'password': x['password'],
                    'email': x['email']
                }, users)

        signup_users = []

        for user in prepared_user_data:
            response = requests.post(self.get_url('/api/user/'), data=user)
            data = self.jsonify_response(response)
            data['password'] = user['password'] # needed for login
            assert response.status_code, 201
            signup_users.append(data)

        return signup_users


    def signin_users(self, users):
        for user in users:
            payload = {'username': user['username'], 'password': user['password']}
            response = requests.post(self.get_url('/api/login/'), data=payload)
            assert response.status_code, 200
            data = self.jsonify_response(response)
            user['token'] = data['token']

        return users
