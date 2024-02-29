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

# Masters entities
CANDY = 'S'
LAVA_SHOES = 'J'

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

# Assignment 3 constants
GAME_FILE = 'games/masters2.txt'
TASK = 2

TILE_COLOURS = {
    LAVA: '#FFA384',
    WALL: '#EFE7BC',
    EMPTY: '#E7F2F8',
    DOOR: '#B99095'
}

ENTITY_COLOURS = {
    COIN: '#f6c324',
    POTION: '#B5E5CF',
    HONEY: '#F8EA8C',
    APPLE: '#E42256',
    WATER: '#74BDCB',
    PLAYER: 'pink',
    CANDY: 'pink',
    LAVA_SHOES: 'orange',
}

THEME_COLOUR = '#C1E1C1'

BANNER_FONT = ('Courier', 45)
HEADING_FONT = ('Courier', 28)
TEXT_FONT = ('Courier', 18)

MAZE_WIDTH = 600
MAZE_HEIGHT = 600
INVENTORY_WIDTH = 200
STATS_HEIGHT = 100

TILE_IMAGES = {
    WALL: 'wall.png',
    EMPTY: 'grass.png',
    LAVA: 'lava.png',
    DOOR: 'door.png',
}

ENTITY_IMAGES = {
    COIN: 'coin.png',
    POTION: 'potion.png',
    HONEY: 'honey.png',
    APPLE: 'apple.png',
    WATER: 'water.png',
    PLAYER: 'player.png',
    CANDY: 'candy.png',
    LAVA_SHOES: 'shoes.png'
}
