import os

# -*- coding: utf-8 -*-
# available languages
LANGUAGES = {
    'fr': 'Français',
    'en': 'English'
}

STRIPE_KEYS = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY'],
    'endpoint_secret': os.environ['ENDPOINT_SECRET']
}


SQLALCHEMY_DATABASE_URI = 'sqlite:///vimebook.db'
