from __future__ import annotations
from typing import Optional
from a2_support import UserInterface, TextInterface
from constants import *

# Replace these <strings> with your name, student number and email address.
__author__ = "Lucas Hicks, s4744008"
__email__ = "lucas.hicks@uqconnect.edu.au"

# Before submission, update this tag to reflect the latest version of the
# that you implemented, as per the blackboard changelog.
__version__ = 1.1

#  Constants
ENTITY = 'E'
MIN_STAT = 0
INVENTORY_FORMAT = 'Inventory(initial_items=[{}])'
TILE_TYPES = {
    WALL: 'Wall()',
    LAVA: 'Lava()',
    DOOR: 'Door()'
}

ENTITIES_LIST = {
    COIN: 'Coin(({}))',
    POTION: 'Potion(({}))',
    HONEY: 'Honey(({}))',
    APPLE: 'Apple(({}))',
    WATER: 'Water(({}))',
    PLAYER: '',
}

HEALTH_DECREASE = -1
HUNGER_DECREASE = 1
THIRST_DECREASE = 1

DOOR_NAME = 'Door'

ITEM_NAMES = ('Potion', 'Coin', 'Water', 'Apple', 'Honey')
ITEM_START = 'i '
INPUT_MESSAGE = 'Enter game file: '
MOVE_MESSAGE = '\nEnter a move: '
WRONG_ITEM_NAME = '\nNo item with that name!\n'
MAZE_STRING = 'Maze: {}\nItems: {}\nPlayer start: {}'


def load_game(filename: str) -> list['Level']:
    """ Reads a game file and creates a list of all the levels in order.

    Parameters:
        filename: The path to the game file

    Returns:
        A list of all Level instances to play in the game
    """
    levels = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('Maze'):
                _, _, dimensions = line[5:].partition(' - ')
                dimensions = [int(item) for item in dimensions.split()]
                levels.append(Level(dimensions))
            elif len(line) > 0 and len(levels) > 0:
                levels[-1].add_row(line)
    return levels


class Tile:
    """Abstract class representing the floor for a (row,column) position."""
    DMG = 0
    _blocking = False
    _id = ABSTRACT_TILE

    def is_blocking(self) -> bool:
        """Returns boolean of whether the tile is blocking."""
        return self._blocking

    def damage(self) -> int:
        """Returns the damage done if the player steps on the tile."""
        return self.DMG

    def get_id(self) -> str:
        """Gets the id of the tile."""
        return self._id

    def __str__(self) -> str:
        """Returns the string representation of the tile (ID)"""
        return self.get_id()

    def __repr__(self) -> str:
        """Returns the text to create a new instance of this class."""
        return f"{type(self).__name__}()"


class Wall(Tile):
    """A Tile subclass that is blocking."""
    _blocking = True
    _id = WALL


class Empty(Tile):
    """A Tile subclass that is essentially nothing."""
    _id = EMPTY


class Lava(Tile):
    """A Tile subclass that does increased damage to the player."""
    DMG = LAVA_DAMAGE
    _id = LAVA


class Door(Tile):
    """A Tile subclass that starts as blocking, but can become non-blocking."""

    def __init__(self) -> None:
        """Constructs a door tile."""
        self._blocking = True
        self._id = DOOR

    def unlock(self) -> None:
        """Unlocks the door, changing the instance's id to that of an empty
        tile and changes the tile to become non-blocking.
        """
        self._blocking = False
        self._id = EMPTY


class Entity:
    """Abstract class for all entities in the game"""
    ID = ENTITY

    def __init__(self, position: tuple[int, int]) -> None:
        """Constructs an item based on (x, y) coordinates.

        Parameters:
            position: x, y coordinates for entity position.
        """
        self._position = position

    def get_position(self) -> tuple[int, int]:
        """Returns the position of the entity."""
        return self._position

    def get_name(self) -> str:
        """Returns the name of the class"""
        return type(self).__name__

    def get_id(self) -> str:
        """Returns the ID of the entity"""
        return self.ID

    def __str__(self) -> str:
        """Returns the string representation of the entity (ID)."""
        return self.get_id()

    def __repr__(self) -> str:
        """Returns the text to create a new instance of this class."""
        return f"{self.get_name()}({str(self._position)})"


class DynamicEntity(Entity):
    """Abstract class that inherits from entity which provides functionality
    for all entities that can move.
    """
    ID = DYNAMIC_ENTITY

    def set_position(self, new_position: tuple[int, int]) -> None:
        """Sets a new position for an entity

        Parameters:
            new_position: x, y coordinates for entity's new position.
        """
        self._position = new_position


class Inventory:
    """An inventory contains and manages a collection of items."""

    def __init__(
        self, initial_items: Optional[list[Item, ...]] = None
    ) -> None:
        """Creates an inventory based on an optional list of initial items

        Parameters:
            initial_items (optional): list of initial items in the inventory
        """
        self._storage = {}
        if initial_items:
            for item in initial_items:
                self.add_item(item)

    def add_item(self, item: Item) -> None:
        """Adds an item instance to the inventory

        Parameters:
            item: Item object to be added to the inventory
        """
        # Either appends value to array in dict or creates an entry in dict
        if item.get_name() in self._storage:
            self._storage[item.get_name()].append(item)
        else:
            self._storage[item.get_name()] = [item]

    def get_items(self) -> dict[str, list[Item, ...]]:
        """(dict) Returns a dictionary mapping of the inventory's items"""
        return self._storage

    def remove_item(self, item_name: str) -> Optional[Item]:
        """Removes the first instance of an item from the inventory

        Parameters:
            item_name: The name of an item that could exist in the inventory

        Returns:
            The representation of the item object is returned if the object
            was removed, otherwise, none is returned
        """

        # Checks if item exists in inventory
        if item_name not in self._storage:
            return None

        removed_item = self._storage[item_name][0]
        del self._storage[item_name][0]

        # Removes key-value pair in dictionary if value array is empty
        if not self._storage[item_name]:
            self._storage.pop(item_name)
        return removed_item

    def check_item(self, item_name: str) -> bool:
        """Returns true if the item exists in the inventory

        Parameters:
            item_name: The name of an item
        """
        return item_name in self.get_items()

    def get_first_item(self, item_name: str) -> Item:
        """Returns the first instance of a given item in the inventory

        Parameters:
            item_name: The name of an item
        """
        return self.get_items()[item_name][0]

    def __str__(self) -> str:
        """Returns string containing information about the quantities of each
         item type in the inventory"""
        output = ''
        for item_name in self._storage:
            output += f"\n{item_name}: {len(self._storage[item_name])}"
        # Removes the new line at the start of output
        return output[1:]

    def __repr__(self) -> str:
        """Returns a string that could be used to create an instance of
        inventory with the same items that it currently contains"""
        items = ''
        for item_name in self._storage:
            for item in self._storage[item_name]:
                items += repr(item) + ', '
        return INVENTORY_FORMAT.format(items[:-2])


class Player(DynamicEntity):
    """A dynamic entity that is controlled by the user, and has hunger,
    thirst and health stats"""
    ID = PLAYER

    def __init__(self, position: tuple[int, int]) -> None:
        """Creates a player instance based on an initial position

        Parameters:
            position: tuple containing x and y coordinates for player start
        """
        super().__init__(position)
        self._inventory = Inventory()
        self._health = 100
        self._hunger = 0
        self._thirst = 0

    def get_hunger(self) -> int:
        """Returns the current hunger of the player"""
        return self._hunger

    def get_thirst(self) -> int:
        """Returns the current thirst of the player"""
        return self._thirst

    def get_health(self) -> int:
        """Returns the current health of the player"""
        return self._health

    def change_hunger(self, amount: int) -> None:
        """Changes the player's hunger by a given amount

        Parameters:
            amount: amount to alter the player's hunger by
        """
        self._hunger += amount

        # Cap player hunger between 0 and 10
        self._hunger = \
            MAX_HUNGER if self._hunger > MAX_HUNGER else self._hunger
        self._hunger = MIN_STAT if self._hunger < MIN_STAT else self._hunger

    def change_thirst(self, amount: int) -> None:
        """Changes the player's thirst by a given amount

        Parameters:
            amount: amount to alter the player's thirst by
        """
        self._thirst += amount

        # Cap player thirst between 0 and 10
        self._thirst = \
            MAX_THIRST if self._thirst > MAX_THIRST else self._thirst
        self._thirst = MIN_STAT if self._thirst < MIN_STAT else self._thirst

    def change_health(self, amount: int) -> None:
        """Changes the player's health by a given amount

        Parameters:
            amount: amount to alter the player's health by
        """
        self._health += amount

        # Cap player health between 0 and 100
        self._health = MAX_HEALTH if self._health > MAX_HEALTH else self._health
        self._health = MIN_STAT if self._health < MIN_STAT else self._health

    def get_inventory(self) -> Inventory:
        """Returns the player's inventory instance"""
        return self._inventory

    def add_item(self, item: Item) -> None:
        """Adds a given item to the player's inventory instance

        Parameters:
            item: Item object to be added to the inventory
        """
        self.get_inventory().add_item(item)

    def use_item(self, item_name: str) -> None:
        """Consumes and applies an item from the player's inventory

        Parameters:
            item_name: name of the item to be used
        """
        item = self.get_inventory().get_first_item(item_name)
        item.apply(self)
        # Coins can't be removed from the inventory
        if item_name != 'Coin':
            self.get_inventory().remove_item(item_name)


class Item(Entity):
    """Entity subclass that provides functionality for all items"""
    ID = ITEM

    def apply(self, player: Player) -> None:
        """Applies the item's effect to the player, if any

        Parameters:
            player: instance of the Player class
        """
        raise NotImplementedError


class Potion(Item):
    """Potion item that increases player health by 20"""
    ID = POTION

    def apply(self, player: Player) -> None:
        """Increases the player's health by 20

        Parameters:
            player: instance of the Player class
        """
        player.change_health(POTION_AMOUNT)


class Coin(Item):
    """A coin item that doesn't affect the player's stats"""
    ID = COIN

    def apply(self, player: Player) -> None:
        """Applies the coins effect to the player (nothing)

        Parameters:
            player: instance of the Player class
        """
        return None


class Water(Item):
    """Water item that decreases player thirst by 5"""
    ID = WATER

    def apply(self, player: Player) -> None:
        """Decreases the player's thirst by 5

        Parameters:
            player: instance of the Player class
        """
        player.change_thirst(WATER_AMOUNT)


class Food(Item):
    """Abstract class for all food items in the game"""
    ID = FOOD
    FOOD_AMOUNT = 0

    def apply(self, player: Player) -> None:
        """Decreases a player's hunger by a certain amount

        Parameters:
            player: instance of the Player class
        """
        player.change_hunger(self.FOOD_AMOUNT)


class Apple(Food):
    """Apple item that decreases player hunger by 1"""
    ID = APPLE
    FOOD_AMOUNT = APPLE_AMOUNT


class Honey(Food):
    """Honey item that decreases player hunger by 5"""
    ID = HONEY
    FOOD_AMOUNT = HONEY_AMOUNT


class Maze:
    """An object that contains the layout and types of tiles in the maze"""

    def __init__(self, dimensions: tuple[int, int]) -> None:
        """Creates an empty maze instance based on row and column dimensions

        Parameters:
            dimensions: tuple with number of rows and columns in the maze
        """
        self._dimensions = dimensions
        self._layout = []
        self._door = None

    def get_dimensions(self) -> tuple[int, int]:
        """Returns a tuple of the row and column dimensions of the maze"""
        return self._dimensions

    def add_row(self, row: str) -> None:
        """Adds a row of tiles to the maze, given a string of Tile IDs

        Parameters:
            row: string containing a row of Tile IDs
        """
        row_list = []
        # Creates tile instances based on row string
        for tile in row:
            # Only adds tiles to maze, and not entities
            row_list.append(
                eval(TILE_TYPES[tile]) if tile in TILE_TYPES else Empty()
            )
        self._layout.append(row_list)

    def get_tiles(self) -> list[list[Tile]]:
        """Returns the layout of the maze"""
        return self._layout

    def unlock_door(self) -> None:
        """Unlocks the door in the maze"""
        for row in self._layout:
            for tile in row:

                if tile.get_id() == DOOR:
                    tile.unlock()
                    return None
        # Method is exited once the door is unlocked (only one door)

    def get_layout(self) -> list[str]:
        """Returns the layout of the maze"""
        return self._layout

    def get_tile(self, position: tuple[int, int]) -> Tile:
        """Returns the tile instance in the maze at a given position

        Parameters:
            position: tuple with x and y coordinates
        """
        return self._layout[position[0]][position[1]]

    def __str__(self) -> str:
        """Returns the string representation of the maze. Each line in the
        output is a row in the maze which is a line of Tile IDs"""
        layout = ''
        for row in self._layout:
            row_print = ''

            for tile in row:
                row_print += str(tile)
            layout += f"{row_print}\n"

        # Removes new line (\n) in layout string
        return layout[:-1]

    def get_name(self) -> str:
        """Returns the name of the class object"""
        return type(self).__name__

    def __repr__(self) -> str:
        """Returns a string that could create another instance of Maze with
        the same dimensions as the current maze instance"""
        return f"{self.get_name()}({str(self._dimensions)})"


class Level:
    """An object that keeps track of the maze and entities in a level"""

    def __init__(self, dimensions: tuple[int, int]) -> None:
        """Creates a level with an empty maze instance based on row and column
         dimensions, along with no player or items

         Parameters:
            dimensions: tuple with number of rows and columns in the maze
         """
        self._maze = Maze(dimensions)
        self._entities = {}
        self._player_position = None

    def get_maze(self) -> Maze:
        """Returns the level's maze instance"""
        return self._maze

    def attempt_unlock_door(self) -> None:
        """Unlocks the door if no coins remain in the level"""
        for item_key in self._entities:
            # Method is exited if a coin is found
            if self._entities[item_key].get_id() == COIN:
                return None

        # Door is unlocked if no coins are present
        self.get_maze().unlock_door()
        return None

    def add_row(self, row: str) -> None:
        """Adds tiles and entities to the level

        Parameters:
            row: A row of Tile and Entity IDs to place in the level's row
        """
        self.get_maze().add_row(row)
        row_num = len(self.get_maze().get_layout()) - 1
        # Uses pos and row_num to calculate position
        for pos, item in enumerate(row):
            if item in ENTITIES_LIST:
                # Handles player start and addition of entities

                if item == PLAYER:
                    self.add_player_start((row_num, pos))
                else:
                    self.add_entity((row_num, pos), item)

    def add_entity(self, position: tuple[int, int], entity_id: str) -> None:
        """Adds or replaces an entity at a given position in the level

        Parameters:
            position: tuple containing x and y coordinates
            entity_id: ID of the entity type to be added
        """
        entity = eval(ENTITIES_LIST[entity_id].format(position))
        self._entities[position] = entity

    def get_dimensions(self) -> tuple[int, int]:
        """Returns a tuple of the number of rows and columns in the maze"""
        return self.get_maze().get_dimensions()

    def get_items(self) -> dict[tuple[int, int], Item]:
        """Returns a mapping of position to the item at that position for all
        items in the maze"""
        return self._entities

    def remove_item(self, position: tuple[int, int]) -> None:
        """Removes an item at a specific position in the maze

        Preconditions:
            Item instance exists at position

        Parameters:
            position: tuple containing x and y coordinates
        """
        del self._entities[position]

    def add_player_start(self, position: tuple[int, int]) -> None:
        """Adds the start position for the player in this level

        Parameters:
            position: tuple containing x and y coordinates
        """
        self._player_position = position

    def get_player_start(self) -> Optional[tuple[int, int]]:
        """Returns the start position for the player for this level"""
        return self._player_position

    def get_name(self) -> str:
        """Returns the name of the class"""
        return type(self).__name__

    def __str__(self) -> str:
        """Returns a string representation for this level, containing the
        maze, the items in the maze and the player's start"""
        return MAZE_STRING.format(
            str(self.get_maze()),
            self.get_items(),
            str(self.get_player_start())
            )

    def __repr__(self) -> str:
        """Returns a string that could create another level instance with the
        same dimensions as this level instance"""
        return f"{self.get_name()}({self.get_dimensions()})"


class Model:
    """Class that is used by the controller to modify the game state. This
    class keeps track of the player and the level instances"""
    def __init__(self, game_file: str) -> None:
        """Creates a model instance from the given game_file

        Parameters:
            game_file: path to a file containing game information
        """
        self._game_file = game_file
        self._levels = load_game(self._game_file)
        self._level_num = 0
        self._player = Player(self.get_level().get_player_start())

        self._move_counter = 1
        self._level_up_move = None

    def has_won(self) -> bool:
        """Returns true if the game has been won"""
        return self._level_num == len(self._levels)

    def has_lost(self) -> bool:
        """Returns true if the game has been lost"""
        if self.get_player().get_health() == MIN_STAT:
            return True
        if self.get_player().get_hunger() == MAX_HUNGER:
            return True
        if self.get_player().get_thirst() == MAX_THIRST:
            return True
        return False

    def get_level(self) -> Level:
        """Returns the current level"""
        return self._levels[self._level_num]

    def level_up(self) -> None:
        """Changes the level to the next level, if one exists"""
        self._level_up_move = self._move_counter
        self._level_num += 1

        if not self.has_won():
            # Sets player position to new player start
            new_pos = self.get_level().get_player_start()
            self.get_player().set_position(new_pos)

    def did_level_up(self) -> bool:
        """Returns true if the player leveled up from the last turn"""
        return self._level_up_move == self._move_counter

    def _update_stats(self, tile: Tile) -> None:
        """Updates the player's stats, given the tile they land on

        Parameters:
            tile: instance of Tile
        """
        # Gain 1 thirst and hunger after every 5 moves
        if not (self._move_counter - 1) % 5:
            self.get_player().change_hunger(HUNGER_DECREASE)
            self.get_player().change_thirst(THIRST_DECREASE)

        self.get_player().change_health(HEALTH_DECREASE - tile.damage())

    def get_name(self) -> str:
        """Returns the name of the class"""
        return type(self).__name__

    def _out_of_maze(self, position: tuple[int, int]) -> bool:
        """Returns true if the given position is outside the maze dimensions

        Parameters:
            position: tuple containing x and y coordinates
        """
        try:
            self.get_current_maze().get_tile(position)
            return False
        except IndexError:
            self.level_up()
            return True

    def move_player(self, delta: tuple[int, int]) -> None:
        """Moves the player by a certain amount (delta)

        Parameters:
            delta: tuple containing values for row and column change
        """
        player_pos = self.get_player_position()
        position = (delta[0]+player_pos[0], delta[1]+player_pos[1])

        # Checks if player has finished the level
        if self._out_of_maze(position):
            return None

        tile = self.get_current_maze().get_tile(position)
        if not tile.is_blocking():
            self.attempt_collect_item(position)
            self.get_player().set_position(position)
            self._move_counter += 1
            self._update_stats(tile)
        return None

    def attempt_collect_item(self, position: tuple[int, int]) -> None:
        """Collects an item at a given position if one exists. Also unlocks
        the door if all coins have been collected

        Parameters:
            position: tuple containing x and y coordinates
        """
        # Checks if item exists at a given position
        if position in self.get_current_items():
            # Adds item to inventory and removes it from level
            self.get_player().add_item(
                self.get_current_items()[position])
            self.get_level().remove_item(position)

        # Attempts to unlock the door, since all coins could be collected
        self.get_level().attempt_unlock_door()

    def get_player(self) -> Player:
        """Returns the player in the game"""
        return self._player

    def get_player_stats(self) -> tuple[int, int, int]:
        """Returns a tuple containing the stats of the player in the game"""
        return (self.get_player().get_health(),
                self.get_player().get_hunger(),
                self.get_player().get_thirst()
                )

    def get_player_inventory(self) -> Inventory:
        """Returns the player's inventory"""
        return self.get_player().get_inventory()

    def get_player_position(self) -> tuple[int, int]:
        """Returns the players current position in the maze"""
        return self.get_player().get_position()

    def get_current_maze(self) -> Maze:
        """Returns the maze for the current level"""
        return self.get_level().get_maze()

    def get_current_items(self) -> dict[tuple[int, int], Item]:
        """Returns a dictionary mapping a position to each item in the maze"""
        return self.get_level().get_items()

    def __str__(self) -> str:
        """Returns a string that could create a new model instance with the
        same game file as the current instance."""
        return f"{type(self).__name__}('{self._game_file}')"

    def __repr__(self) -> str:
        """Returns a string that could create a new model instance with the
        same game file as the current instance."""
        return self.__str__()


class MazeRunner:
    """Controller class that maintains instances of model and view"""
    def __init__(self, game_file: str, view: UserInterface) -> None:
        """Creates a new MazeRunner game with a given view and a model
        loaded using the given game_file.

        Parameters:
            game_file: path to a file containing game information.
            view: instance of view class that provides the text interface.
        """
        self._file = game_file
        self._model = Model(game_file)
        self._view = view

    def _get_model(self) -> Model:
        """Returns the model instance."""
        return self._model

    def _user_turn(self) -> None:
        """Facilitates a user's turn, handling whether a user choose to
        move or use an item."""
        user_input = prompt_user()

        # Handles whether player is using an item or moving
        if user_input in MOVE_DELTAS:
            self._get_model().move_player(MOVE_DELTAS[user_input])
        else:
            self._try_item(user_input[2:].capitalize())

    def _try_item(self, item_name: str) -> None:
        """Handles the logic for a user choosing to use an item. This method
        checks to see if it exists and whether the user has one in its
        inventory, and prints out the relevant message.

        Parameters:
            item_name: name of the item to be used.
        """
        # Checks for invalid item
        if item_name not in ITEM_NAMES:
            print(WRONG_ITEM_NAME)
        # Checks if item is available in inventory
        elif self._get_model().get_player_inventory().check_item(item_name):
            self._get_model().get_player().use_item(item_name)
        else:
            print(ITEM_UNAVAILABLE_MESSAGE)

    def play(self) -> None:
        """Executes the entire game until a win or loss occurs."""
        while True:
            # Draws interface and begins a player's turn
            self._view.draw(
                self._get_model().get_current_maze(),
                self._get_model().get_level().get_items(),
                self._get_model().get_player_position(),
                self._get_model().get_player_inventory(),
                self._get_model().get_player_stats()
            )
            self._user_turn()

            # Checks if player has won or lost after each turn
            if self._get_model().has_won():
                print(WIN_MESSAGE)
                return None

            if self._get_model().has_lost():
                print(LOSS_MESSAGE)
                return None


def prompt_user() -> str:
    """Prompts the user for a move and returns it."""
    while True:
        user_input = input(MOVE_MESSAGE)
        if user_input in MOVE_DELTAS or user_input[:2] == ITEM_START:
            # Stops asking once user input is valid
            return user_input


def main():
    """Entry-point to gameplay."""
    file = input(INPUT_MESSAGE)
    view = TextInterface()
    mazerunner = MazeRunner(file, view)
    mazerunner.play()


if __name__ == '__main__':
    main()
