from __future__ import annotations
from random import choice, seed

VOCAB_FILE = "vocab.txt"
ANSWERS_FILE = "answers.txt"
CORRECT = "🟩"
MISPLACED = "🟨"
INCORRECT = "⬛"
UNSEEN = " "

# seed(1001.2022)

def load_words(filename: str) -> tuple[str,...]:
	""" Loads all words from the file with the given name.

	Parameters:
		filename (str): The name of the file to load from. Each word must be on
						a separate line.

	Returns:
		tuple<str>: A tuple containing all the words in the file.
	"""
	with open(filename, 'r') as file:
		words = [line.strip() for line in file.readlines()]
	return tuple(words)

def choose_word(words: tuple[str,...]) -> str:
	""" Chooses a word at random from words.

	Parameters:
		words (tuple<str>): The words to choose from.

	Returns:
		str: A word chosen at random from words.
	"""
	return choice(words)
