# Installation

First, be sure to sign up for a [Stripe account](https://stripe.com/) (the payment platform) and go to the [API page](https://dashboard.stripe.com/account/apikeys) to get your keys.

In this readme, I'm using 3 sample keys:

    PUBLISHABLE_KEY=pk_test_4aZnwTrOtTfNSxs8KtI1a3LC
    SECRET_KEY=sk_test_4aZnq9QgKUcJ2cPp9dGaidOT
    ENDPOINT_SECRET=whsec_AjrfPgBKPZhCnU5grqtuhDnXU5OYA9zf

## Pip / python env

    pip install virtualenv
    virtualenv -p /usr/bin/python3 env
    . ./env/bin/activate
    pip install -r requirements.txt

## Create db

    PUBLISHABLE_KEY=pk_test_4aZnwTrOtTfNSxs8KtI1a3LC SECRET_KEY=sk_test_4aZnq9QgKUcJ2cPp9dGaidOT ENDPOINT_SECRET=whsec_AjrfPgBKPZhCnU5grqtuhDnXU5OYA9zf python
    from app import db,app
    app.app_context().push()
    db.create_all()

You can use <Ctrl-d> to exit the python shell. The database should have been created under the `instance/` directory.

## Translations

### Extract strings to translate

    pybabel extract -F babel.cfg -o messages.pot ./templates

### Update messages.po

    pybabel update -i messages.pot -d translations

### Finally compile

    pybabel compile -d translations

## Run

Depending on the keys, it will run in production/test mode for stripe.

    ENDPOINT_SECRET="whsec_AjrfPgBKPZhCnU5grqtuhDnXU5OYA9zf" PUBLISHABLE_KEY=pk_test_4aZnwTrOtTfNSxs8KtI1a3LC SECRET_KEY=sk_test_4aZnq9QgKUcJ2cPp9dGaidOT python app.py

The dev server should be listening on http://localhost:5000

# Supervisor

Of course, you need to replace the test keys by the live one.

    [program:vimebook]
    environment = PATH="/home/vimebook/python/vim-for-humans-website/env/bin:%(ENV_PATH)s",PUBLISHABLE_KEY="pk_test_4aZnwTrOtTfNSxs8KtI1a3LC",SECRET_KEY="sk_test_4aZnq9QgKUcJ2cPp9dGaidOT",ENDPOINT_SECRET="whsec_AjrfPgBKPZhCnU5grqtuhDnXU5OYA9zf"
    command = /home/vimebook/python/vim-for-humans-website/gunicorn_start.sh ; Command to start app
    user = vimebook ; User to run as
    stdout_logfile = /home/vimebook/python/vim-for-humans-website/log/gunicorn_supervisor.log ; Where to write log messages
    redirect_stderr = true ; Save stderr in the same log

Supervisorctl commands:

    supervisorctl reread
    supervisorctl update

# Good reads

- https://eff.iciently.com/blog/stripe_checkout.html
- http://www.jeffknupp.com/blog/2014/01/18/python-and-flask-are-ridiculously-powerful/
- http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiv-i18n-and-l10n
- https://www.safaribooksonline.com/blog/2013/11/27/flask-internationalization-and-localization/
- http://damyanon.net/
