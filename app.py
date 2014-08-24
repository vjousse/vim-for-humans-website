import os
from flask import Flask, render_template, request, url_for, redirect
from flask.ext.sqlalchemy import SQLAlchemy
import stripe

stripe_keys = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vimebook.db'
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('index.html', key=stripe_keys['publishable_key'])

@app.route('/download')
def download():
    return render_template('download.html', key=stripe_keys['publishable_key'])

@app.route('/confirm/<int:amount>')
def confirm(amount):
    return render_template('confirm.html', amount=amount/100)

@app.route('/charge', methods=['POST'])
def charge():
    #{'id': 'tok_14TwY1KRgapzZVSgDU5fI3Io', 'livemode': False, 'email': 'vincent@jousse.org', 'card': {'id': 'card_14TwY1KRgapzZVSgD4JHoVDa', 'brand': 'Visa', 'address_zip': None, 'exp_month': 12, 'address_city': None, 'name': 'vincent@jousse.org', 'customer': None, 'country': 'US', 'address_state': None, 'fingerprint': 'KNmudQJYDGikF2dE', 'address_line2': None, 'last4': '4242', 'exp_year': 2023, 'address_line1': None, 'funding': 'credit', 'address_country': None, 'object': 'card'}, 'type': 'card', 'created': 1408631297, 'used': False, 'object': 'token'}

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

    return redirect(url_for('confirm', amount=amountInCents))

class Download(db.Model):
    __tablename__ = 'purchase'
    uuid = db.Column(db.String, primary_key=True)
    email = db.Column(db.String)


if __name__ == '__main__':
    app.run(debug=True)
