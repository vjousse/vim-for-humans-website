import os
import uuid
from datetime import datetime

import stripe
from flask import (
    Flask,
    abort,
    g,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_babel import Babel, gettext
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from config import LANGUAGES, SQLALCHEMY_DATABASE_URI, STRIPE_KEYS, UPDATES

app = Flask(__name__, static_folder="static")
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

stripe.api_key = STRIPE_KEYS["secret_key"]
endpoint_secret = STRIPE_KEYS["endpoint_secret"]


def get_locale():
    """Direct babel to use the language defined in the session."""
    return g.get("current_lang", "fr")


babel = Babel(app, default_locale="fr")
babel.init_app(app, locale_selector=get_locale)


@app.before_request
def before():
    if request.view_args and "lang_code" in request.view_args:
        if request.view_args["lang_code"] not in LANGUAGES.keys():
            return abort(404)
        g.current_lang = request.view_args["lang_code"]
        request.view_args.pop("lang_code")


@app.route("/robots.txt")
@app.route("/sitemap.xml")
@app.route("/favicon.ico")
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@app.route("/")
def root():
    return redirect(url_for("index", lang_code="fr"))


@app.route("/<lang_code>")
def index():
    download_number = Download.query.count()
    donations = Download.query.filter(Download.price > 0).all()
    donation_number = len(donations)
    total_donation = 0
    for donation in donations:
        total_donation += donation.price

    result = (
        db.session.query(
            func.max(Download.price).label("max"), func.min(Download.price).label("min")
        )
        .filter(Download.price > 0)
        .one()
    )

    framasoft_amount = "{:.2f}".format(total_donation * 0.20)

    average_donation = 0
    if not donation_number == 0:
        average_donation = total_donation / donation_number

    current_lang = g.get("current_lang", "fr")

    return render_template(
        "index.html",
        key=STRIPE_KEYS["publishable_key"],
        download_number=download_number,
        donation_number=donation_number,
        framasoft_amount=framasoft_amount,
        average_donation="{:.2f}".format(average_donation),
        last_update=UPDATES[current_lang],
        max=result.max,
        min=result.min,
    )


@app.route("/download/<download_uuid>/<name>.<format>")
def download_file_compat(download_uuid, name, format):
    return redirect(
        url_for(
            "download_file",
            lang_code="fr",
            download_uuid=download_uuid,
            name=name,
            format=format,
        )
    )


@app.route("/<lang_code>/download/<download_uuid>/<name>.<format>")
def download_file(download_uuid, name, format):
    download = Download.query.get(download_uuid)
    if format not in ["pdf", "epub", "mobi"]:
        abort(404)

    if name not in ["vim-for-humans", "vim-pour-les-humains"]:
        abort(404)

    download.count += 1
    db.session.commit()

    return send_from_directory(
        os.path.join(app.static_folder, "book", g.get("current_lang", "fr")),
        "{}.{}".format(gettext("vim-for-humans"), format),
    )


@app.route("/<lang_code>/confirm/<download_uuid>")
def confirm(download_uuid):
    download = Download.query.get(download_uuid)

    amount = None

    if download:
        amount = download.price

    new = False

    return render_template(
        "confirm.html",
        amount=amount,
        uuid=download_uuid,
        known_email=download.email,
        new=new,
    )


@app.route("/<lang_code>/confirm-other/<download_uuid>")
def confirm_free(download_uuid):
    return render_template("confirm-other.html", uuid=download_uuid)


@app.route("/<lang_code>/cancel")
def cancel():
    return render_template("cancel.html")


@app.route("/stripe_webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data.decode("utf-8")
    received_sig = request.headers.get("Stripe-Signature", None)

    event = None

    try:
        event = stripe.Webhook.construct_event(payload, received_sig, endpoint_secret)
    except ValueError as e:
        print("Error while decoding event!")
        print(e)
        return "Bad payload", 400
    except stripe.error.SignatureVerificationError as e:
        print("Invalid signature!")

        print(e)
        return "Bad signature", 400

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        print(session)

        download = Download(
            uuid=session["client_reference_id"],
            email=session["customer_details"]["email"],
            price=session["amount_total"] / 100,
            lang=g.get("current_lang"),
        )

        db.session.add(download)
        db.session.commit()

    return ("", 200)


@app.route("/<lang_code>/charge", methods=["POST"])
def charge():
    # Amount in cents
    amount = float(request.form["amount"])
    amountInCents = int(amount * 100)
    download_uuid = str(uuid.uuid4())

    if amount != 0.0:
        session = stripe.checkout.Session.create(
            client_reference_id=download_uuid,
            payment_method_types=["card"],
            line_items=[
                {
                    "quantity": 1,
                    "price_data": {
                        "unit_amount": amountInCents,
                        "currency": "eur",
                        "product_data": {
                            "name": "Vim for humans",
                        },
                    },
                }
            ],
            mode="payment",
            success_url=url_for(
                "confirm",
                download_uuid=download_uuid,
                lang_code=g.get("current_lang", "fr"),
                _external=True,
            ),
            cancel_url=url_for(
                "cancel", lang_code=g.get("current_lang", "fr"), _external=True
            ),
        )

        return render_template(
            "charge.html",
            key=STRIPE_KEYS["publishable_key"],
            checkout_session_id=session.id,
        )

    else:
        download = Download(uuid=download_uuid, lang=g.get("current_lang"))

        db.session.add(download)
        db.session.commit()

        return redirect(
            url_for(
                "confirm_free",
                download_uuid=download_uuid,
                lang_code=g.get("current_lang", "fr"),
            )
        )


@app.route("/<lang_code>/subscribe/<download_uuid>", methods=["POST"])
def subscribe_with_download(download_uuid):
    email = request.values["email"]
    email_number = Email.query.filter_by(email=email).count()

    new = False
    if email_number == 0:
        # Save subscription
        emailObject = Email(
            email=email, download_id=download_uuid, lang=g.get("current_lang", "fr")
        )

        db.session.add(emailObject)
        db.session.commit()
        new = True

    return render_template(
        "confirm-other.html", email=email, uuid=download_uuid, new=new
    )


class Download(db.Model):
    __tablename__ = "download"
    uuid = db.Column(db.String, primary_key=True)
    email = db.Column(db.String)
    price = db.Column(db.Float, default=0)
    count = db.Column(db.Integer, default=0)
    lang = db.Column(db.String, default="fr")
    #: Timestamp for when this instance was created, in UTC
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    #: Timestamp for when this instance was last updated (via the app), in UTC
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Email(db.Model):
    __tablename__ = "email"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    lang = db.Column(db.String, default="fr")
    download_id = db.Column(db.String, db.ForeignKey("download.uuid"), nullable=True)
    #: Timestamp for when this instance was created, in UTC
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    #: Timestamp for when this instance was last updated (via the app), in UTC
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


if __name__ == "__main__":
    app.run(debug=True)
