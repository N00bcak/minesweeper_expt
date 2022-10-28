# We keep all of our external imports here. We should only have internal imports within the other files.

import random
from itertools import product
import tkinter as tk
from tkinter import messagebox
import json

# Defaults and constants:

MINE_SYMBOL = "M"
FLAG_SYMBOL = "F"

DEFAULT_CONFIG = {
	"colors": {
		0: "white", 1: "blue", 2: "green", 
        3: "red", 4: "purple", 5: "orange",
        6: "grey", 7: "maroon", 8: "turquoise",
        MINE_SYMBOL: "black"
	},
	"difficulty_settings": {
		"Easy": {
			"height": 10,
			"width": 10,
			"mines": 15
		},
		"Medium": {
			"height": 15,
			"width": 15,
			"mines": 40
		},
		"Hard": {
			"height": 20,
			"width": 20,
			"mines": 99
		},
		"Custom": {
			"height": None,
			"width": None,
			"mines": None
		}
	}
}

CUSTOM_ENTRY_FIELDS = ["Height: ", "Width: ", "Mines: "]


# Wrapper function to help pack the function for calling on-demand.
def on_click(f, *args):
    def g(_):
        print(f"The wrapper function on_click was called with arguments {f.__name__} {args}")
        # try:
        f(*args)
        # except TypeError:
        #     print(f"on_click wrapper function reported argument errors! {f.__name__} {args}")
    return g

class ConfigEditor:

	# This object interacts with the config.txt of the project. 
	# Needless to say, if there is no config file, create it and populate it with the default config settings.

	def create_cfg(self):
		with open(self.config_file, "w") as f:
			f.write(json.dumps(DEFAULT_CONFIG))

	def read_cfg(self):
		try:
			with open(self.config_file, "r") as f:
				cfg = json.loads(f.read())
			return cfg
		except Exception:
			self.create_cfg()
			return DEFAULT_CONFIG

	def find_cfg(self, query_string: str):
		
		# This gives me an idea for a class that traverses through generic JSON dictionaries.

		query_result = self.options_dict
		layer_list = query_string.split(".")
		for layer in layer_list:
			query_result = query_result[layer]
		
		return query_result

	def edit_cfg(self, query_string: str, edit_dict: dict):
		
		# TODO: Find out how to filter out unwanted entries.
		# For now we will simply hack together a clumsy json dict.
		
		for edit_key, edit_value in edit_dict.items():
			try:
				self.find_cfg(query_string)[edit_key] = edit_value
			except KeyError:
				pass

		with open(self.config_file, "w") as f:
			f.write(json.dumps(self.options_dict))

	# The class takes in a file name which contains your game configuration.
	def __init__(self, config_file = "config.txt"):
		self.config_file = config_file
		self.options_dict = self.read_cfg()