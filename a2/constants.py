LAVA = 'L'
WALL = '#'
EMPTY = ' '
DOOR = 'D'

PLAYER = 'P'

ITEM = 'I'
FOOD = 'F'
DYNAMIC_ENTITY = 'DE'
ABSTRACT_TILE = 'AT'

COIN = 'C'
POTION = 'M'
HONEY = 'H'
APPLE = 'A'
WATER = 'W'

APPLE_AMOUNT = -1
HONEY_AMOUNT = -5
WATER_AMOUNT = -5
POTION_AMOUNT = 20

UP = 'w'
DOWN = 's'
LEFT = 'a'
RIGHT = 'd'
MOVE_DELTAS = {
    UP: (-1, 0),
    DOWN: (1, 0),
    LEFT: (0, -1),
    RIGHT: (0, 1),
}

MAX_HEALTH = 100
MAX_HUNGER = 10
MAX_THIRST = 10
LAVA_DAMAGE = 5

WIN_MESSAGE = 'Congratulations! You have finished all levels and won the game!'
LOSS_MESSAGE = 'You lose :('
ITEM_UNAVAILABLE_MESSAGE = '\nYou don\'t have any of that item!\n'
