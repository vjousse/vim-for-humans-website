# Installation

## Pip / python env

    pip install virtualenv
    virtualenv -p /usr/bin/python3 env
    . ./env/bin/activate
    pip install -r requirements.txt

## Create db

    PUBLISHABLE_KEY=pk_test_4aZnwTrOtTfNSxs8KtI1a3LC SECRET_KEY=sk_test_4aZnq9QgKUcJ2cPp9dGaidOT python
    from app import tdb
    db.create_all()

## Run

    PUBLISHABLE_KEY=pk_test_4aZnwTrOtTfNSxs8KtI1a3LC SECRET_KEY=sk_test_4aZnq9QgKUcJ2cPp9dGaidOT python app.py

# Supervisor

Off course, you need to replace the test keys by the live one.

    [program:vimebook]
    environment = PUBLISHABLE_KEY="pk_test_4aZnwTrOtTfNSxs8KtI1a3LC",SECRET_KEY="sk_test_4aZnq9QgKUcJ2cPp9dGaidOT"
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
