import datetime
from os import environ
import copy

import firebase_admin
import requests
from dotenv import load_dotenv
from firebase_admin import credentials, firestore

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

load_dotenv()

paintings_ref = db.collection(environ.get('FIREBASE_PAINTINGS_COLLECION'))
techniques_ref = db.collection(environ.get('FIREBASE_TECHNIQUES_COLLECTION'))
collections_ref = db.collection(environ.get('FIREBASE_COLLECTIONS_COLLECTION'))


def get_data(sheet_name):
	api_key = environ.get('GOOGLE_API_KEY')
	req = requests.get(f'https://sheets.googleapis.com/v4/spreadsheets/{environ.get("GOOGLE_SHEET_ID")}'
					   f'/values/{sheet_name}!A:Z?key={api_key}')

	if req.status_code != 200:
		print(f'-- error - {req.json()} --')

	return req.json().get('values')[0], req.json().get('values')[1:]


def populate_collection(keys, values, primary_key: int, ref, exclude_primary_key):
	raw_values = copy.deepcopy(values)

	if exclude_primary_key:
		keys.pop(primary_key)
		for value in values:
			value.pop(primary_key)

	for i in range(len(values)):
		doc_ref = ref.document(raw_values[i][primary_key])
		doc_ref.set({key: values[i][j] for j, key in enumerate(keys)})

	print(f'-- db updated {datetime.datetime.now()} --')


def populate_collections():
	keys, values = get_data("Collections")

	clean_collection(collections_ref)
	populate_collection(keys, values, 0, collections_ref, False)


def populate_techniques():
	keys, values = get_data('Techniques')

	clean_collection(techniques_ref)
	populate_collection(keys, values, 0, techniques_ref, True)


def populate_paintings():
	keys, values = get_data('Tableaux')

	for value in values:
		for i, key in enumerate(keys):
			if key == 'archived':
				value[i] = True if value[i] == "TRUE" else False
			elif key == 'technique':
				value[i] = techniques_ref.document("crayon").get().to_dict()["name"]

	clean_collection(paintings_ref)
	populate_collection(keys, values, 0, paintings_ref, True)


def clean_collection(ref):
	docs = ref.stream()

	for doc in docs:
		ref.document(doc.id).delete()
