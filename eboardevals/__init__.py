import os

import csh_ldap
from flask import Flask, render_template, redirect
from flask_migrate import Migrate
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from flask_sqlalchemy import SQLAlchemy

# Create the initial Flask Object

app = Flask(__name__)

# Check if deployed on OpenShift, if so use environment.
if os.path.exists(os.path.join(os.getcwd(), "config.py")):
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.py"))
else:
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.env.py"))

auth = OIDCAuthentication(app, issuer=app.config["OIDC_ISSUER"],
                          client_registration_info=app.config["OIDC_CLIENT_CONFIG"])

# Create a connection to CSH LDAP
_ldap = csh_ldap.CSHLDAP(
    app.config['LDAP_BIND_DN'], app.config['LDAP_BIND_PASS'])

# Initalize the SQLAlchemy object and add models.
# Make sure that you run the migrate task before running.
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# pylint: disable=C0413
from eboardevals.utils import before_request
from eboardevals.ldap import ldap_get_eboard


@app.route("/")
@auth.oidc_auth
@before_request
def main(info=None):
    if info['is_eboard']:
        return redirect("/admin")
    return redirect("/new")


@app.route("/new")
@auth.oidc_auth
@before_request
def new(info=None):
    eboard = ldap_get_eboard()
    return render_template(
        "new.html",
        info=info,
        eboard=eboard
    )


@app.route("/admin")
@auth.oidc_auth
@before_request
def admin(info=None):
    if info['is_eboard']:
        return render_template(
            "admin.html",
            info=info
        )


@app.route("/archive")
@auth.oidc_auth
@before_request
def archive(info=None):
    if info['is_eboard']:
        return render_template(
            "archive.html",
            info=info
        )
