import json
import os
from enum import Enum

from api import get_data


class TranslationCol(Enum):
	fr = 1
	en = 2


def generate_translations(lang_col: int, lang_name: str):
	data = get_data('Traductions')[1:]
	translations = {}

	for row in data[0]:
		section = row[0].split('.')[0]
		key = '.'.join(row[0].split('.')[1:])
		existing_section = translations.get(section)

		if len(row) != 3:
			row.append("")

		if not existing_section:
			translations[section] = {}
		translations[section][key] = row[lang_col]

	directory = 'translations'
	if not os.path.exists(directory):
		os.makedirs(directory)

	filename = f"{directory}/{lang_name}.json"
	with open(filename, "w") as outfile:
		json.dump(translations, outfile)

	return filename
