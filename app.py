import os, uuid
from flask import Flask, render_template, request, url_for, redirect, send_from_directory
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
import stripe

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vimebook.db'
db = SQLAlchemy(app)

stripe_keys = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/')
def index():
    return render_template('index.html', key=stripe_keys['publishable_key'])

@app.route('/download')
def download():
    return render_template('download.html', key=stripe_keys['publishable_key'])

@app.route('/confirm/<int:amount>')
def confirm(amount):
    return render_template('confirm.html', amount=amount/100)

@app.route('/confirm/')
def confirmfree():
    return render_template('confirm-free.html')

@app.route('/charge', methods=['POST'])
def charge():

    # Amount in cents
    amount = float(request.form['amount'])
    amountInCents = int(amount*100)

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
                uuid=str(uuid.uuid4()),
                email=request.form['email'],
                price=amount)

        db.session.add(download)
        db.session.commit()
        return redirect(url_for('confirm', amount=amountInCents))

    else:

        download = Download(uuid=str(uuid.uuid4()))
        db.session.add(download)
        db.session.commit()
        return redirect(url_for('confirmfree'))


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
