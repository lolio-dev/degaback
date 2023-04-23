from os import environ

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

from api import populate_collections, populate_paintings, populate_techniques
from translations import generate_translations, TranslationCol

app = Flask(__name__, static_folder='/translations')
app.secret_key = environ.get('FLASK_SECRET_KEY')
auth = HTTPBasicAuth()

load_dotenv()

username = environ.get("ADMIN_USERNAME")
password = environ.get("ADMIN_PASSWORD")

users = {
	username: generate_password_hash(password)
}


@auth.verify_password
def verify_password(username, password):
	if username in users and check_password_hash(users.get(username), password):
		return username


@app.route("/")
@auth.login_required
def index():
	status = request.args.get("status")
	sheet_id = environ.get('GOOGLE_SHEET_ID')

	if status == "success":
		flash("Base de donnée correctement mise à jour", "success")
		return redirect(request.path)
	elif status == "error":
		flash("Une erreur est survenue, veuillez réessayer ulterirement ou contacter l'administrateur", "danger")
		return redirect(request.path)

	return render_template("index.html", sheet_id=sheet_id)


@app.route("/updatedb/<col_name>")
@auth.login_required
def update_db(col_name):
	try:
		match col_name:
			case "paintings":
				populate_paintings()
			case "techniques":
				populate_techniques()
			case "collections":
				populate_collections()
	except Exception:
		return redirect(url_for('index', status="error"))

	return redirect(url_for('index', status="success"))


@app.route("/downloadtrads/<lang>")
@auth.login_required
def download_traductions(lang):
	filename = generate_translations(TranslationCol[lang].value, lang)

	return send_file(filename, as_attachment=True)


if __name__ == '__main__':
	app.run()
