import os, uuid
from flask import Flask, render_template, request, url_for, redirect, send_from_directory, g, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babel import Babel
from sqlalchemy import func 
from datetime import datetime
from functools import reduce
from config import LANGUAGES
import stripe

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vimebook.db'
db = SQLAlchemy(app)
babel = Babel(app, default_locale='fr')

stripe_keys = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

@babel.localeselector
def get_locale():
    """Direct babel to use the language defined in the session."""
    return g.get('current_lang', 'fr')


@app.before_request
def before():
    if request.view_args and 'lang_code' in request.view_args:
        if request.view_args['lang_code'] not in LANGUAGES.keys():
            return abort(404)
        g.current_lang = request.view_args['lang_code']
        request.view_args.pop('lang_code')

@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/')
def root():
    return redirect(url_for('index', lang_code='fr'))

@app.route('/<lang_code>')
def index():
    return render_template('index.html', key=stripe_keys['publishable_key'])

@app.route('/download')
def download():
    download_number = Download.query.count()
    donations = Download.query.filter(Download.price>0).all()
    donation_number = len(donations)
    total_donation = 0
    for donation in donations:
        total_donation += donation.price

    result = db.session \
            .query(func.max(Download.price).label("max"), func.min(Download.price).label("min")) \
            .filter(Download.price > 0) \
            .one()

    framasoft_amount = "{:.2f}".format(total_donation * 0.20)
    average_donation = total_donation / donation_number
    return render_template('download.html', \
            key=stripe_keys['publishable_key'], \
            download_number = download_number, \
            donation_number = donation_number, \
            framasoft_amount = framasoft_amount, \
            average_donation = "{:.2f}".format(average_donation), \
            max = result.max, \
            min = result.min)

@app.route('/download/<download_uuid>/<name>.<format>')
def downloadfile(download_uuid, name, format):
    download = Download.query.get(download_uuid)
    if format != 'pdf' and format != 'epub' and format != 'mobi':
        format = 'pdf'

    download.count += 1
    db.session.commit()

    return send_from_directory(os.path.join(app.static_folder, 'book'), 'vim-pour-les-humains.{}'.format(format))

@app.route('/<lang_code>/confirm/<download_uuid>')
def confirm(download_uuid):
    download = Download.query.get(download_uuid)
    return render_template('confirm.html', amount=download.price, uuid=download_uuid)

@app.route('/<lang_code>/confirm-other/<download_uuid>')
def confirmfree(download_uuid):
    download = Download.query.get(download_uuid)
    return render_template('confirm-free.html', uuid=download_uuid)

@app.route('/charge', methods=['POST'])
def charge():

    # Amount in cents
    amount = float(request.form['amount'])
    amountInCents = int(amount*100)

    download_uuid = str(uuid.uuid4())

    if(amount != 0.0):
        customer = stripe.Customer.create(
            email=request.form['email'],
            card=request.form['stripeToken']
        )

        charge = stripe.Charge.create(
            customer=customer.id,
            amount=amountInCents,
            currency='eur',
            description='Vim pour les humains'
        )

        download = Download(
                uuid=download_uuid,
                email=request.form['email'],
                price=amount)

        db.session.add(download)
        db.session.commit()
        return redirect(url_for('confirm', download_uuid=download_uuid))

    else:

        download = Download(uuid=download_uuid)
        db.session.add(download)
        db.session.commit()
        return redirect(url_for('confirmfree', download_uuid=download_uuid))


class Download(db.Model):
    __tablename__ = 'download'
    uuid = db.Column(db.String, primary_key=True)
    email = db.Column(db.String)
    price = db.Column(db.Float, default=0)
    count = db.Column(db.Integer, default=0)
    #: Timestamp for when this instance was created, in UTC
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    #: Timestamp for when this instance was last updated (via the app), in UTC
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


if __name__ == '__main__':
    app.run(debug=True)
