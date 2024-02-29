from __future__ import annotations
from typing import Optional
from a2_support import UserInterface, TextInterface
from constants import *


class Tile:
    """ An abstract class providing base functionality for tiles on a maze. """
    _id = ABSTRACT_TILE

    def is_blocking(self) -> bool:
        """ Returns True iff a player cannot move onto the tile. """
        return False
    
    def damage(self) -> int:
        """ Returns damage done to the player when they step on the tile. """
        return 0
    
    def get_id(self) -> str:
        """ Returns the ID for this tile. Should be a single character for each
            subclass.
        """
        return self._id

    def __str__(self) -> str:
        """ Returns a string representation of this Tile. """
        return self.get_id()
    
    def __repr__(self) -> str:
        """ Returns a computer representation of this Tile. """
        return f"{self.__class__.__name__}()"

class Empty(Tile):
    """ A tile representing an empty square. Players can pass over an empty tile
        with no damage.
    """
    _id = EMPTY

class Lava(Tile):
    """ A tile representing a square filled with lava. A player can step on lava
        but it causes some damage.
    """
    _id = LAVA

    def damage(self) -> int:
        return LAVA_DAMAGE

class Wall(Tile):
    """ A simple blocking tile. """
    _id = WALL

    def is_blocking(self) -> bool:
        return True

class Door(Tile):
    """ A door in the maze. A door starts as blocking, but must be unlocked by
        the player before they can walk through it.
    """
    _name = 'Door'
    _id = DOOR

    def __init__(self) -> None:
        super().__init__()
        self._blocking = True

    def is_blocking(self) -> bool:
        return self._blocking
    
    def get_id(self) -> str:
        return self._id if self.is_blocking() else EMPTY
    
    def unlock(self) -> None:
        """ Unlocks the door by setting it to be non-blocking. """
        self._blocking = False



class Entity:
    """ Abstract base class for any entity."""
    _id = 'E'
    def __init__(self, position: tuple[int, int]) -> None:
        """Sets up the entity at the provided location.
        
        Parameters:
            postion: (row, column) position of the entity.
        """
        self._position = position

    def get_position(self) -> tuple[int, int]:
        """ Returns the (row, column) position of this entity. """
        return self._position

    def get_name(self) -> str:
        """ Returns the name of this entity's class. """
        return self.__class__.__name__
    
    def get_id(self) -> str:
        """ Returns the single character id of this entity's class. """
        return self._id
    
    def __str__(self) -> str:
        """ Returns the string representation of this entity. """
        return self._id
    
    def __repr__(self):
        """ Returns the string representation of this entity. """
        return f"{self.__class__.__name__}({self.get_position()})"


class Item(Entity):
    """ Abstract class providing an interface for all items in the game. """
    _id = ITEM

    def apply(self, player: 'Player') -> None:
        """ Applies the item's effect to the given player.
        
        Parameters:
            player: The player for which this item's effect will be applied.
        """
        raise NotImplementedError


class Potion(Item):
    """ A potion restores the players HP by 20 when applied. """
    _id = POTION

    def apply(self, player: 'Player') -> None:
        """ Increases players HP by 20. """
        player.change_health(POTION_AMOUNT)


class Coin(Item):
    """ Coins are collected by the player to allow the door to be unlocked. """
    _id = COIN

    def apply(self, player: 'Player') -> None:
        """ Coin has no effect on the player. """
        return


class Food(Item):
    """ An abstract class that provides base functionality for food items. A
        food item decreases the player's hunger by a set amount depending on the
        type of food.
    """
    _id = FOOD
    _amount = 0

    def apply(self, player: 'Player') -> None:
        """ Changes player's hunger; amount depends on the type of food. """
        player.change_hunger(self._amount)


class Apple(Food):
    """ Apples decrease the players hunger by 1. """
    _id = APPLE
    _amount = APPLE_AMOUNT


class Honey(Food):
    """ Honey decreases the players hunger by 5. """
    _id = HONEY
    _amount = HONEY_AMOUNT


class Water(Item):
    """ Water decreases the player's thirst by 5. """
    _id = WATER

    def apply(self, player: 'Player') -> None:
        """ Decreases player's thirst by 20. """
        player.change_thirst(WATER_AMOUNT)


class Inventory:
    """ A collection of items. """
    def __init__(self, initial_items: Optional[list[Item]] = None) -> None:
        """ Sets up this inventory with the initial items (if provided). Else
            sets up a new empty inventory.
        
        Parameters:
            initial_items: An optional list of initial items to put in inventory
        """
        self._items = {}
        if initial_items is not None:
            for item in initial_items:
                self.add_item(item)
    
    def add_item(self, item: Item) -> None:
        """ Adds the given item to the inventory.
        
        Parameters:
            item: The item to add
        """
        items = self._items.get(item.get_name(), [])
        items.append(item)
        self._items[item.get_name()] = items

    def get_items(self) -> dict[str, list[Item]]:
        """ Returns the a dictionary mapping item names to the instances of the
            item with that name in the inventory.
        """
        return self._items

    def remove_item(self, item_name: str) -> Optional['Item']:
        """ Removes one instance of the item with the given name from inventory,
            if one exists.

        Parameters:
            item_name: The name of the item to remove one instance of.
        
        Returns:
            The removed item, if one exists, else None.

        """
        items = self._items.get(item_name)
        if items is None or items == []:
            return None
        else:
            item = items.pop(0)
            if self._items.get(item_name) == []:
                del self._items[item_name]
            return item
    
    def __str__(self):
        text = [f'{name}: {len(items)}' for name, items in self._items.items()]
        return '\n'.join(text)
    
    def __repr__(self):
        items = []
        for name in self._items:
            items.extend(self._items.get(name))
        return f'Inventory(initial_items={items})'


class DynamicEntity(Entity):
    """ An abstract class that provides base functionality for entities which
        can move around the maze.

        Note: they'll extend this in A3 to have direction and an Enemy subclass.
    """
    _id = DYNAMIC_ENTITY
    
    def set_position(self, new_position: tuple[int, int]) -> None:
        """ Updates the position of this entity.
        
        Parameters:
            new_position: The new position at which to place the entity.
        """
        self._position = new_position


class Player(DynamicEntity):
    """ The player in the game. """
    _id = PLAYER

    def __init__(self, position: tuple[int, int]) -> None:
        """ Sets up this player.
        
        Parameters:
            position: Starting position for this player
        """
        super().__init__(position)
        self._health = MAX_HEALTH
        self._hunger = 0
        self._thirst = 0
        self._inventory = Inventory()
    
    def get_hunger(self) -> int:
        """ Returns the player's current hunger. """
        return self._hunger

    def get_thirst(self) -> int:
        """ Returns the player's current thirst. """
        return self._thirst

    def get_health(self) -> int:
        """ Returns the player's current HP. """
        return self._health

    def _change_amount(self, initial: int, change: int, bound: int) -> int:
        """ A helper method for changing an amount while bounding it between
            0 and some upper limit.
        
        Parameters:
            initial: Initial value to change
            change: The amount by which to change the value (within bounds)
            bound: The upper bound for this change
        
        Returns:
            The updated amount bound by 0 and the upper bound.
        """
        return max(min(initial + change, bound), 0)

    def change_hunger(self, amount: int) -> None:
        """ Changes the hunger value for this player and caps at bounds.
        
        Parameters:
            amount: The amount to add to the current hunger.
        """
        self._hunger = self._change_amount(self._hunger, amount, MAX_HUNGER)
    
    def change_thirst(self, amount: int) -> None:
        """ Changes the thirst value for this player and caps at bounds.
        
        Parameters:
            amount: The amount to add to the current thirst.
        """
        self._thirst = self._change_amount(self._thirst, amount, MAX_THIRST)

    def change_health(self, amount: int) -> None:
        """ Changes the HP value for this player and caps at bounds.
        
        Parameters:
            amount: The amount to add to the current HP.
        """
        self._health = self._change_amount(self._health, amount, MAX_HEALTH)

    def add_item(self, item: Item) -> None:
        """ Adds the given item to this players inventory.
        
        Parameters:
            item: The item to add.
        """
        self._inventory.add_item(item)
    
    def get_inventory(self) -> Inventory:
        """ Returns the players inventory. """
        return self._inventory


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

class Maze:
    """ Models a single map for one level. Only includes ground information,
        excluding information about entities. """
    TILES = {
        WALL: Wall,
        EMPTY: Empty,
        DOOR: Door,
        LAVA: Lava,
    }

    def __init__(self, dimensions: tuple[int, int]) -> None:
        """Sets up an empty maze of given dimensions.
        
        Parameters:
            dimensions: (#rows, #columns)
        """
        self._dimensions = dimensions
        self._tiles = []
    
    def get_dimensions(self) -> tuple[int, int]:
        """ Returns the dimensions of this maze. """
        return self._dimensions
    
    def add_row(self, row: str) -> None:
        """ Adds a row of tiles to the maze.
        
        Parameters:
            row: String of the tile IDs from which to construct Tile instances.
        """
        # If there is an entity in a spot, assume the ground underneath is empty
        self._tiles.append([self.TILES.get(tile, Empty)() for tile in row])

    def get_tiles(self) -> list[list[Tile]]:
        """ Returns the Tile instances in this maze. Each element is a row of
            Tile instances in order.
        """
        return self._tiles
    
    def unlock_door(self) -> None:
        """ Unlocks any doors that exist in the maze. """
        for row in self._tiles:
            for tile in row:
                if isinstance(tile, Door):
                    tile.unlock()
    
    def get_tile(self, position: tuple[int, int]) -> Tile:
        """ Returns the Tile instance at the given position.
        
        Parameters:
            position: The (row, column) position from which to find the tile.
        """
        row, col = position
        return self._tiles[row][col]
    
    def __str__(self) -> str:
        """ Returns the string representation of this maze. """
        return '\n'.join(
            [''.join([tile.get_id() for tile in row]) for row in self._tiles]
        )
    
    def __repr__(self) -> str:
        """ Returns the computer representation of this maze. """
        return f"Maze({self._dimensions})"


class Level:
    """ Models one level of a game, including maze and entities. """
    ENTITIES = {
        COIN: Coin,
        POTION: Potion,
        APPLE: Apple,
        HONEY: Honey,
        WATER: Water,
    }

    def __init__(self, dimensions: tuple[int, int]) -> None:
        """ Sets up a new level with empty maze and no items or player.
        
        Parameters:
            dimensions: The (#rows, #columns) in the maze for this level.
        """
        self._maze = Maze(dimensions)
        self._items = {} # Maps positions to Item instances
        self._player_start = None
    
    def get_maze(self) -> Maze:
        """ Returns the Maze instance for this level. """
        return self._maze
    
    def _contains_coins(self) -> bool:
        """ Returns True iff there are any more coins left in this level. """
        return any([item.get_id() == COIN for item in self._items.values()])

    def attempt_unlock_door(self) -> None:
        """ Unlocks the doors in the maze if there are no coins remaining. """
        if not self._contains_coins():
            self._maze.unlock_door()
    
    def add_row(self, row: str) -> None:
        """ Adds the tiles and entities from the row to this level.
        
        Parameters:
            row: A string of tile or entity IDs.
        """
        row_num = len(self._maze.get_tiles())
        self._maze.add_row(row)
        for col_num, char in enumerate(row):
            self.add_entity((row_num, col_num), char)
    
    def add_entity(self, position: tuple[int, int], entity_id: str) -> None:
        """ Adds a new entity to this level.
        
        Parameters:
            position: The (row, column) position at which to add the entity.
            entity_id: The ID of the entity to add.
        """
        if self.ENTITIES.get(entity_id) is not None:
            self._items[position] = self.ENTITIES.get(entity_id)(position)
        if entity_id == PLAYER:
            self.add_player_start(position)

    def get_dimensions(self) -> tuple[int, int]:
        """ Returns the (#rows, #columns) in the level maze. """
        return self._maze.get_dimensions()
    
    def get_items(self) -> dict[tuple[int, int], Item]:
        """ Returns a mapping from position to the Item at that position for all
            items currently in this level.
        """
        return self._items

    def remove_item(self, position: tuple[int, int]) -> None:
        """ Deletes the item from the given position.
        
        Pre-conditions:
            There must be an item existing at the given position.
        
        Parameters:
            position: the (row, column) position from which to delete an item.
        """
        del self._items[position]
    
    def add_player_start(self, position: tuple[int, int]) -> None:
        """ Adds the start position for the player in this level.
        
        Parameters:
            position: The position at which the player starts.
        """
        self._player_start = position
    
    def get_player_start(self) -> tuple[int, int]:
        """ Returns the starting position of the player for this level. """
        return self._player_start

    def __str__(self):
        """ Returns a string representation of this level. """
        maze, items, player_start = self._maze, self._items, self._player_start
        return f"Maze: {maze}\nItems: {items}\nPlayer start: {player_start}"
    
    def __repr__(self):
        """ Returns a computer representation of this level. """
        return f"Level({self.get_dimensions()})"


class Model:
    """ The overall model for a game of MazeRunner """
    def __init__(self, game_file: str) -> None:
        """ Constructs a new game.
        
        Parameters:
            game_file: The file containing the levels for this game.
        """
        self._levels = load_game(game_file)
        self._level_num = 0
        self._player = Player(self.get_level().get_player_start())
        self._won = False
        self._did_level_up = False
        self._num_moves = 0
        self._game_file = game_file

    def has_won(self) -> bool:
        """ Returns True iff the game has been won (i.e. all levels have been
            completed).
        """
        return self._won
    
    def has_lost(self) -> bool:
        """ Returns True iff the game has been lost (HP too low or hunger or
            thirst too high.
        """
        return self._player.get_health() <= 0 \
            or self._player.get_hunger() >= MAX_HUNGER \
            or self._player.get_thirst() >= MAX_THIRST

    def get_level(self) -> Level:
        """ Returns the current level. """
        return self._levels[self._level_num]
    
    def did_level_up(self) -> True:
        """ Returns True if the player just moved to the next level on the
            previous turn.
        """
        return self._did_level_up

    def level_up(self) -> None:
        """ Changes the level to the next level from the file. If no more levels
            remain, the player has won the game.
        """
        self._level_num += 1
        if self._level_num >= len(self._levels):
            self._won = True
        else:
            self._player.set_position(self.get_level().get_player_start())
            self._did_level_up = True

    def move_player(self, delta: tuple[int, int]) -> None:
        """ Tries to move the player by the requested amount. Levels up if the
            user finishes the maze, """
        self._did_level_up = False
        old_pos = self._player.get_position()
        position = row, col = old_pos[0] + delta[0], old_pos[1] + delta[1]
        max_row, max_col = self.get_level().get_dimensions()

        # Check if player has escaped the maze
        if (row < 0 or row >= max_row or col < 0 or col >= max_col) and \
            isinstance(self.get_current_maze().get_tile(old_pos), Door):
            self.level_up()

        # Move player if tile is non-blocking and update stats
        else:
            tile = self.get_current_maze().get_tile(position)
            if not tile.is_blocking():
                self._num_moves += 1
        
                if self._num_moves % 5 == 0:
                    self._player.change_hunger(1)
                    self._player.change_thirst(1)
                self._player.change_health(-1 - tile.damage())

                self._player.set_position(position)
                self.attempt_collect_item(position)
    
    def attempt_collect_item(self, position: tuple[int, int]) -> None:
        """ Collect the item at the given position if one exists. Unlock door if
            all coins have been collected.
        
        Parameters:
            position: The position from which to attempt to collect an item.
        """
        item = self.get_level().get_items().get(position)
        if item is not None:
            self._player.add_item(item)
            self.get_level().remove_item(position)
        self.get_level().attempt_unlock_door()
        
    def get_player(self) -> Player:
        """ Returns the player in the game. """
        return self._player

    def get_player_stats(self) -> tuple[int, int, int]:
        """ Returns the players stats as (HP, hunger, thirst). """
        player = self.get_player()
        return (player.get_health(), player.get_hunger(), player.get_thirst())
    
    def get_player_inventory(self) -> Inventory:
        """ Returns the players inventory. """
        return self.get_player().get_inventory()
    
    def get_current_maze(self) -> Maze:
        """ Returns the Maze for the current level. """
        return self.get_level().get_maze()

    def get_current_items(self) -> dict[tuple[int, int], Item]:
        """ Returns a mapping from positions to the items that exist on those
            positions in the current maze. """
        return self.get_level().get_items()

    def __str__(self):
        return f"Model('{self._game_file}')"
    
    def __repr__(self):
        return str(self)


class MazeRunner:
    """ Controller class for a game of MazeRunner """
    def __init__(self, game_file: str, view: UserInterface) -> None:
        """ Sets up initial game state
        
        Parameters:
            game_file: Path to the file from which the game levels are loaded
            view: A subclass of Interface to manage the display of information
        """
        self._model = Model(game_file)
        self._view = view

    def _redraw(self) -> None:
        """ Redraws the entire view based on the current model state. """
        model = self._model
        self._view.draw(
            model.get_current_maze(),
            model.get_current_items(),
            model.get_player().get_position(),
            model.get_player_inventory(),
            model.get_player_stats()
        )

    def _user_prompt(self) -> None:
        """ Prompts the user for a move and updates model state accordingly. """
        move = input('\nEnter a move: ')
        self._handle_move(move)

    def _handle_move(self, move: str) -> None:
        """ Handles a model update after a single move. Reprompts if move is
            invalid.

        Parameters:
            move: The users input from a move prompt.
        """
        # Player has attempted to move
        if move in (UP, DOWN, LEFT, RIGHT):
            self._model.move_player(MOVE_DELTAS.get(move))
        
        # Player has attempted to use an item
        elif len(move) > 1 and move.split()[0] == 'i':
            item_name = move.partition(' ')[-1]
            item = self._model.get_player().get_inventory().remove_item(item_name)
            if item is not None:
                item.apply(self._model.get_player())
            else:
                print('\nNo item with that name!\n')
    
        # Invalid; reprompt
        else:
            self._user_prompt()

    def play(self):
        """ Executes the entire game until a win or loss occurs. """
        while True:
            self._redraw()
            self._user_prompt()

            if self._model.has_won():
                print(WIN_MESSAGE)
                break
            elif self._model.has_lost():
                print(LOSS_MESSAGE)
                break

def main():
    """ Entry-point to gameplay """
    view = TextInterface()
    game_file = input('Enter game file: ')
    maze_runner = MazeRunner(game_file, view)
    maze_runner.play()
    print(maze_runner._model._levels[0])

if __name__ == '__main__':
    main()

