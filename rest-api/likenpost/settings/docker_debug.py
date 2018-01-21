from likenpost.settings.docker import *

INSTALLED_APPS += [
    'silk',
]

MIDDLEWARE = [
    'silk.middleware.SilkyMiddleware',
] + MIDDLEWARE
