import os
from flask import Flask, render_template, request
import stripe

stripe_keys = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', key=stripe_keys['publishable_key'])

@app.route('/download')
def download():
    return render_template('download.html', key=stripe_keys['publishable_key'])

@app.route('/charge', methods=['POST'])
def charge():
    #{'id': 'tok_14TwY1KRgapzZVSgDU5fI3Io', 'livemode': False, 'email': 'vincent@jousse.org', 'card': {'id': 'card_14TwY1KRgapzZVSgD4JHoVDa', 'brand': 'Visa', 'address_zip': None, 'exp_month': 12, 'address_city': None, 'name': 'vincent@jousse.org', 'customer': None, 'country': 'US', 'address_state': None, 'fingerprint': 'KNmudQJYDGikF2dE', 'address_line2': None, 'last4': '4242', 'exp_year': 2023, 'address_line1': None, 'funding': 'credit', 'address_country': None, 'object': 'card'}, 'type': 'card', 'created': 1408631297, 'used': False, 'object': 'token'}

    # Amount in cents
    amount = 500

    customer = stripe.Customer.create(
        email='customer@example.com',
        card=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Flask Charge'
    )

    return render_template('charge.html', amount=amount)

if __name__ == '__main__':
    app.run(debug=True)
