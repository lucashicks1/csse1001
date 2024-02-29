"""
Wordle
Assignment 1
Semester 1, 2022
CSSE1001/CSSE7030
"""

from string import ascii_lowercase
from typing import Optional

from a1_support import (
    load_words,
    choose_word,
    VOCAB_FILE,
    ANSWERS_FILE,
    CORRECT,
    MISPLACED,
    INCORRECT,
    UNSEEN,
)


# Replace these <strings> with your name, student number and email address.
__author__ = "Lucas Hicks, s47440085"
__email__ = "lucas.hicks@uqconnect.edu.au"


# Add your functions here


def has_won(guess: str, answer: str) -> bool:
    """
    Returns true if the users guess matches the answer exactly

    Parameters:
    guess (str): the users guess
    answer (str): answer to the wordle game

    Returns:
    bool: whether the user has won or not
    """

    # Checking if the lowercase version of both guess and answer are the same
    if guess.lower() == answer.lower():
        return True
    else:
        return False


def has_lost(guess_number: int) -> bool:
    """ Checks if the player has lost yet

    Returns true if the guess number is greater or
    equal to the maximum number of guesses (6)

    Parameters:
    guess_number (int): Number of guesses the user has had

    Returns:
    bool: whether the user has lost or not
    """
    if guess_number >= 6:
        return True
    else:
        return False


def remove_word(words: tuple[str, ...], word: str) -> tuple[str, ...]:
    """ Returns a copy of the words tuple with the word removed.

    Removes a word from a tuple. This is used to remove an
    answer from the answers tuple ensuring that the same word
    doesn't get selected twice as the answer

    Parameters:
    words (tuple[str,...]): Tuples of words (answers tuple)
    word (str): A six-letter word (answer) which is getting removed

    Returns:
    tuple[str,...]: Modified version of words with word removed
    """
    # Finds index of the word in the tuple
    # Index is used to add two spliced tuples
    position = words.index(word)
    return words[:position] + words[position+1:]


def prompt_user(guess_number: int, words: tuple[str, ...]) -> str:
    """ Prompts user for a guess until it is valid.

    Prompts the user for a guess until there guess is valid.
    A guess must be either:
    - exactly 6 letters long
    - a word in the vocab.txt file
    - a h,k or q (help, keyboard, quit).
    This function then returns a lowercase version of this guess/input

    Parameters:
    guess_number (int): The number of guesses the user has had
    words (tuple[str, ...]): List of valid words that a user can input

    Returns:
    str: lowercase version of the users guess/input
    """
    options = ('k', 'q', 'h')
    while True:
        guess = input(f'Enter guess {guess_number}: ').lower()
        # Checks if the user has chosen to q, ask for help, or check keyboard
        if guess in options:
            return guess
        elif len(guess) != 6:
            print('Invalid! Guess must be of length 6')
        elif guess not in words:
            print('Invalid! Unknown word')
        else:
            return guess


def process_guess(guess: str, answer: str) -> str:
    """ Returns the square reprsentation of a guess

    Function that returns a modified representation of the users guess.
    Each letter in the guess string is replaced with squares.
    Green square - same letter has occurred in the same position as answer.
    Yellow square - same letter has occurred in a different position as answer.
    Black square - letter is not present in the answer

    Parameters:
    guess (str): a users guess (6 letters)
    answer (str): the 6 letter answer for that round

    Returns:
    str: version of guess string with each letter being replaced with squares
    """
    result = list(guess)
    done = []
    for char in guess:
        if char not in done:
            if guess.count(char) == 1:
                # only one instance of the characeter
                if char in answer:
                    if guess.index(char) == answer.index(char):
                        result[result.index(char)] = CORRECT
                    else:
                        result[result.index(char)] = MISPLACED
                else:
                    result[result.index(char)] = INCORRECT
            else:
                # Character occurs multiple times
                position_list = []
                for n in range(len(guess)):
                    if guess[n] == char:
                        position_list.append(n)
                if answer.count(char) > 0:
                    # Character appears in string
                    answer_position = answer.index(char)
                    if answer_position in position_list:
                        result[answer_position] = CORRECT
                        position_list.remove(answer_position)
                    else:
                        result[position_list[0]] = MISPLACED
                        position_list.pop(0)
                for char_position in position_list:
                    result[char_position] = INCORRECT

            done.append(char)

    result = ''.join(x for x in result)
    return result


def update_history(
        history: tuple[tuple[str, str], ...], guess: str,
        answer: str) -> tuple[tuple[str, str], ...]:
    """ Returns a copy of history tuple with the new guess added

    Function that returns a copy of the history tuple with the newest guess and
    its processed form (square form). This function is used to print the users
    guess history after each guess

    Parameters:
    history (tuple[tuple[str,str],...]):
    guess (str): The users guess for that round
    answer (str): The answer for that game

    Returns:
    tuple[tuple[str,str],...]: A version of history with new word and squares
    """
    # Converts to list to allow for changes as list are mutable
    temp_tuple = list(history)
    temp_tuple.append((guess, process_guess(guess, answer)))
    return tuple(temp_tuple)


def print_history(history: tuple[tuple[str, str], ...]) -> None:
    """ Prints out guess history for each round

    Function that prints out the guess history for that round in a
    user-friendly way. It prints out the guess number, along with
    the guess and its square representation.

    Parameters:
    history (tuple[tuple[str,str],...]): Tuple with guess words and squares

    """
    line = '---------------\n'
    # Iterates through guess history, prints guess + squares
    for i in range(len(history)):
        print(line+'Guess '+str(i+1)+':  ' +
              ' '.join(history[i][0])+'\n'+' '*9 + history[i][1])
    # Done for correct spacing
    print(line)


def print_keyboard(history: tuple[tuple[str, str], ...]) -> None:
    """ Prints out the keyboard with known information for each letter

    A function that prints out the 'status' (not attempted, black square,
    yellow square, green square) for each lettter on the keyboard. This is
    printed out in a user friendly way with two columns of letters. If a
    letter appears in more than one of the user's guesses, the 'better'
    square is shown (eg: a green square is shown over a yellow and a yellow
    square would be shown over a black square)

    Parameters:
    history (tuple[tuple[str,str],...]): Tuple with guess words and squares
    """
    letters = {
        'a': UNSEEN,
        'b': UNSEEN,
        'c': UNSEEN,
        'd': UNSEEN,
        'e': UNSEEN,
        'f': UNSEEN,
        'g': UNSEEN,
        'h': UNSEEN,
        'i': UNSEEN,
        'j': UNSEEN,
        'k': UNSEEN,
        'l': UNSEEN,
        'm': UNSEEN,
        'n': UNSEEN,
        'o': UNSEEN,
        'p': UNSEEN,
        'q': UNSEEN,
        'r': UNSEEN,
        's': UNSEEN,
        't': UNSEEN,
        'u': UNSEEN,
        'v': UNSEEN,
        'w': UNSEEN,
        'x': UNSEEN,
        'y': UNSEEN,
        'z': UNSEEN,
    }
    # List used to 'rank' squares -> a lower index equals better square
    # Green > Yellow > Black > Unseen  <--- Square ranking
    options = [CORRECT, MISPLACED, INCORRECT, UNSEEN]
    for guess_pair in history:
        # Iterates through each character in each guess
        for char_index in range(len(guess_pair[0])):
            # If char in iteration is greater than dict
            square = guess_pair[1][char_index]
            char = guess_pair[0][char_index]
            # Checks if square in letters is 'better' than square
            if options.index(square) < options.index(letters[char]):
                letters[char] = square
    print('\nKeyboard information\n'+'-'*12)
    counter = 0  # Counter used as logic for either printing a tab or new line
    # Prints keyboard information in user friendly way
    # Use of ternary operators for spacing
    for key in letters:
        # Determine if newline or tab space is required
        endval = '\n' if counter % 2 else '' if counter == 25 else '\t'
        print(key+': ' + letters[key], end=endval)
        counter += 1
    # Used to format output correctly
    print('')


def update_stats(
        stats: tuple[int, ...], guess_number: int, guess: str,
        answer: str) -> tuple[int, ...]:
    """ Updates stats tuple if users wins or loses

    A function that updates the stats tuple if a user wins or loses a game.
    Each win is broken down into how many guesses it took, whilst a loss is
    simply tallied up

    Parameters:
    stats (tuple[int, ...]): Tuple containing scores for each game
    guess_number (int): Number of guesses the user has used
    guess (str): A users 6 letter guess
    answer (str): String containing the 6 letter answer for that round

    Returns:
    tuple[int,...]: An updated version of the stats tuple with a won/loss added
    """
    templist = list(stats)
    if has_won(guess, answer):
        templist[guess_number-1] += 1
    else:
        templist[6] += 1
    return tuple(templist)


def print_stats(stats: tuple[int, ...]) -> None:
    """ Prints out the stats tuple in a user-friendly way.

    Parameters:
    stats (tuple[int, ...]): Tuple containing scores for each game
    """
    print('\nGames won in:')
    for i in range(6):
        print(str(i+1)+' moves: '+str(stats[i]))
    print('Games lost: '+str(stats[6]))


def play_again() -> bool:
    """ Asks user if they want to play again

    A function that asks a user whether they would like to play another round
    of the game. If the user enters Y or y, they play another round. If they
    enter anything else, the game ends and the program terminates.

    Returns:
    bool: Boolean whether the userepresenting the users choice to play again
    """
    choice = input('Would you like to play again (y/n)? ').lower()
    # Returns true if choice = y, and false if anything else
    return choice == 'y'


def main():
    """ Main game function

    The main function that coordinates the overall gameplay. This function
    utilises many other functions to orchestrate gameplay.
    """
    # Initialising variables used in the game
    stats = (0, 0, 0, 0, 0, 0, 0)
    answers = load_words(ANSWERS_FILE)
    vocab = load_words(VOCAB_FILE)
    # Main program loop -> will break from loop if user doesn't play again
    while True:
        guess_number = 1
        answer = choose_word(answers)
        history = ()
        # Loop for each game
        while True:
            # Loop for each guess
            while True:
                guess = prompt_user(guess_number, vocab)
                # This ensures a guess isn't 'used' when a user enter q,k or h
                if guess == 'q':
                    # User opts to quit
                    quit_option = 1
                    return
                elif guess == 'k':
                    print_keyboard(history)
                elif guess == 'h':
                    print('Ah, you need help? Unfortunate.')
                else:
                    history = update_history(history, guess, answer)
                    print_history(history)
                    break
            if has_won(guess, answer):
                # Used plural version of guesses
                # Spec didn't mention case with 1 guess
                print('Correct! You won in '+str(guess_number)+' guesses!')
                break
            elif has_lost(guess_number):
                print('You lose! The answer was: '+answer)
                break
            guess_number += 1
        stats = update_stats(stats, guess_number, guess, answer)
        print_stats(stats)
        if not play_again():
            break
            # User has chosen to not play again
        else:
            # User is playing again
            # Word is removed from answers
            # Ensures answer is always different
            answers = remove_word(answers, answer)


if __name__ == "__main__":
    main()
