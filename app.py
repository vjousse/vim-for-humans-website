import os
import uuid
from flask import Flask, render_template, request, url_for, redirect, \
                  send_from_directory, g, abort
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel, gettext
from sqlalchemy import func
from datetime import datetime
from config import LANGUAGES, SQLALCHEMY_DATABASE_URI, STRIPE_KEYS
import stripe

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)
babel = Babel(app, default_locale='fr')

stripe.api_key = STRIPE_KEYS['secret_key']


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
@app.route('/favicon.ico')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@app.route('/')
def root():
    return redirect(url_for('index', lang_code='fr'))


@app.route('/<lang_code>')
def index():

    download_number = Download.query.count()
    donations = Download.query.filter(Download.price > 0).all()
    donation_number = len(donations)
    total_donation = 0
    for donation in donations:
        total_donation += donation.price

    result = db.session \
        .query(func.max(Download.price).label("max"),
               func.min(Download.price).label("min")) \
        .filter(Download.price > 0) \
        .one()

    framasoft_amount = "{:.2f}".format(total_donation * 0.20)

    average_donation = 0
    if not donation_number == 0:
        average_donation = total_donation / donation_number

    return render_template(
        'index.html',
        key=STRIPE_KEYS['publishable_key'],
        download_number=download_number,
        donation_number=donation_number,
        framasoft_amount=framasoft_amount,
        average_donation="{:.2f}".format(average_donation),
        max=result.max,
        min=result.min)


@app.route('/download/<download_uuid>/<name>.<format>')
def download_file_compat(download_uuid, name, format):
    return redirect(url_for(
            'download_file', lang_code='fr', download_uuid=download_uuid,
            name=name, format=format
            ))


@app.route('/<lang_code>/download/<download_uuid>/<name>.<format>')
def download_file(download_uuid, name, format):
    download = Download.query.get(download_uuid)
    if format not in ['pdf', 'epub', 'mobi']:
        abort(404)

    if name not in ['vim-for-humans', 'vim-pour-les-humains']:
        abort(404)

    download.count += 1
    db.session.commit()

    return send_from_directory(
        os.path.join(
            app.static_folder,
            'book',
            g.get('current_lang', 'fr')),
        '{}.{}'.format(gettext('vim-for-humans'), format))


@app.route('/<lang_code>/confirm/<download_uuid>')
def confirm(download_uuid):
    download = Download.query.get(download_uuid)
    return render_template(
        'confirm.html', amount=download.price, uuid=download_uuid)


@app.route('/<lang_code>/confirm-other/<download_uuid>')
def confirm_free(download_uuid):
    return render_template('confirm-free.html', uuid=download_uuid)


@app.route('/<lang_code>/cancel')
def cancel():
    return render_template('cancel.html')


@app.route('/<lang_code>/charge', methods=['POST'])
def charge():

    # Amount in cents
    amount = float(request.form['amount'])
    download_uuid = str(uuid.uuid4())

    if(amount != 0.0):

        stripe.checkout.Session.create(
          payment_method_types=['card'],
          line_items=[{
            'name': 'Vim for humans',
            'amount': amount,
            'currency': 'eur',
            'quantity': 1,
          }],
          success_url=url_for(
            'confirm',
            download_uuid=download_uuid,
            lang_code=g.get('current_lang', 'fr')),
          cancel_url=url_for(
            'cancel',
            lang_code=g.get('current_lang', 'fr'))
        )

        download = Download(
                uuid=download_uuid,
                email=request.form['email'],
                price=amount,
                lang=g.get('current_lang'))

        db.session.add(download)
        db.session.commit()

        return redirect(url_for(
            'confirm',
            download_uuid=download_uuid,
            lang_code=g.get('current_lang', 'fr')))

    else:

        download = Download(uuid=download_uuid,
                            lang=g.get('current_lang'))

        db.session.add(download)
        db.session.commit()

        return redirect(
            url_for('confirm_free',
                    download_uuid=download_uuid,
                    lang_code=g.get('current_lang', 'fr')))


class Download(db.Model):
    __tablename__ = 'download'
    uuid = db.Column(db.String, primary_key=True)
    email = db.Column(db.String)
    price = db.Column(db.Float, default=0)
    count = db.Column(db.Integer, default=0)
    lang = db.Column(db.String, default='fr')
    #: Timestamp for when this instance was created, in UTC
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False)
    #: Timestamp for when this instance was last updated (via the app), in UTC
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False)


if __name__ == '__main__':
    app.run(debug=True)
