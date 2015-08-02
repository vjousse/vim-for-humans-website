import os

# -*- coding: utf-8 -*-
# available languages
LANGUAGES = {
    'fr': 'Français',
    'en': 'English'
}

STRIPE_KEYS = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}


SQLALCHEMY_DATABASE_URI = 'sqlite:///vimebook.db'
