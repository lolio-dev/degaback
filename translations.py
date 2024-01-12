import json
import os
from enum import Enum

from api import get_data


class TranslationCol(Enum):
	fr = 1
	en = 2


def generate_translations(lang_col: int):
	raw_data = get_data('Traductions')[1:][0]
	data = {}
	translations = {}

	for row in raw_data:
		try:
			data[row[0]] = row[lang_col]
		except IndexError:
			data[row[0]] = ""

	for key, value in data.items():
		keys = key.split('.')
		current_dict = translations
		for k in keys[:-1]:
			current_dict = current_dict.setdefault(k, {})
		current_dict[keys[-1]] = value

	return translations


def write_to_file(translations, lang_name):
	directory = 'translations'
	if not os.path.exists(directory):
		os.makedirs(directory)

	filename = f"{directory}/{lang_name}.json"

	with open(filename, "w") as outfile:
		json.dump(translations, outfile)

	return filename

generate_translations(2)
