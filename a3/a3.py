import tkinter as tk
from typing import Union, Callable
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk

from a2_solution import *
from a3_support import AbstractGrid
from constants import GAME_FILE, TASK, TILE_COLOURS, ENTITY_COLOURS

# Constants
STATS_WIDTH = INVENTORY_WIDTH + MAZE_WIDTH
BANNER_TEXT = 'MazeRunner'
STAT_HEADINGS = ('HP', 'Hunger', 'Thirst', 'Coins')
OVAL_SCALING = 5
COIN_NAME = 'Coin'
STATS_DIMENSIONS = (2, 4)
RESTART_GAME = 'Restart game'
NEW_GAME = 'New game'
TIMER = '{}m {}s'
NOT_VALID_MESSAGE = 'That game file is not valid'
NEW_GAME_WINDOW_SIZE = '200x150'
QUIT_MESSAGE = 'Are you sure you want to quit?'
WRONG_SAVE = 'That is not a correct save file'
SAVE_TYPES = {
    'stats_open': '<',
    'stats_close': '>',
    'item_separate': ',,'
}
STAT_ROW = 1
HEADING_ROW = 0
COIN_POSITION = (1, 3)


class LevelView(AbstractGrid):
    """ View class that displays the tiles and the entities in the level """

    def draw(
            self,
            tiles: list[list[Tile]],
            items: dict[tuple[int, int], Item],
            player_pos: tuple[int, int]
    ) -> None:
        """Clears and redraws the entire level (maze, entities)

        Parameters:
            tiles:tile instances in the maze
            items: dictionary mapping to position to item instance
            player_pos: current position of player
        """
        self.clear()
        num_rows, num_cols = self._dimensions
        for row in range(num_rows):

            for col in range(num_cols):
                position = (row, col)
                self._draw_asset(position, tiles[row][col].get_id(), True)

        for position in items:
            self._draw_asset(position, items[position].get_id(), False)

        self._draw_asset(player_pos, PLAYER, False)

        self.pack(side=tk.LEFT)

    def _draw_asset(
            self,
            position: tuple[int, int],
            asset_id: str,
            is_tile: bool
    ) -> None:
        """ Draws tile and entity in maze

        Parameters:
            position: Row and column position to find the asset
            asset_id: ID of the asset to add
            is_tile: Boolean representing whether asset is a tile or not
        """
        x_min, y_min, x_max, y_max = self.get_bbox(position)
        if is_tile:
            self.create_rectangle(
                x_min,
                y_min,
                x_max,
                y_max,
                fill=TILE_COLOURS[asset_id]
            )
        else:
            self.create_oval(
                x_min + OVAL_SCALING,
                y_min + OVAL_SCALING,
                x_max - OVAL_SCALING,
                y_max - OVAL_SCALING,
                fill=ENTITY_COLOURS[asset_id]
            )
            self.annotate_position(position, asset_id)


class ImageLevelView(LevelView):
    """Image View class that displays tiles and entities as images"""
    def __init__(
            self,
            master: Union[tk.Tk, tk.Frame],
            dimensions: tuple[int, int],
            size: tuple[int, int],
            **kwargs
    ) -> None:
        """Creates an instance of ImageLevelView

        Parameters:
            master: the tk frame that encapsulates the entire view
            dimensions: Number of rows and columns in the maze
            size: tuple containing width and height of the maze
        """
        super().__init__(master, dimensions, size, **kwargs)
        self._images = {}

    def _generate_image(self, image_id: str, is_tile: bool):
        """Creates an entity/tile image and stores it in self._images

        Parameters:
            image_id: the id of the entity/tile to add
            is_tile: boolean representing whether the asset is a tile
        """
        if is_tile:
            file = f"images/{TILE_IMAGES[image_id]}"
        else:
            file = f"images/{ENTITY_IMAGES[image_id]}"
        size = self.get_cell_size()

        pil_img = Image.open(file)
        pil_img = pil_img.resize(size)

        img = ImageTk.PhotoImage(pil_img)
        self._images[image_id] = img

    def _draw_asset(
            self,
            position: tuple[int, int],
            asset_id: str,
            is_tile: bool
    ) -> None:
        """Uses the stored image to draw an entity/tile on the maze

        Parameters:
            position: x and y position of entity/tile
            id: the id of the entity/tile to add
            is_tile: boolean representing whether the asset is a tile
        """
        x, y = self.get_midpoint(position)

        # Checks whether the image is already created and saved
        if asset_id not in self._images:
            self._generate_image(asset_id, is_tile)

        self.create_image(x, y, image=self._images[asset_id])

    def reset_stored_images(self):
        """Removes all the stored images, allowing for images with different
           dimensions to be created."""
        self._images = {}


class StatsView(AbstractGrid):
    """View class that displays the players stats and amount of coin"""
    def __init__(
            self,
            master: Union[tk.Tk, tk.Frame],
            width: int,
            **kwargs
    ) -> None:
        """Sets up a statsview in the master frame

        Parameters:
            master: the tk frame that encapsulates the entire view
            width: the width of the statsview window
        """
        super().__init__(master, STATS_DIMENSIONS, (width, STATS_HEIGHT), **kwargs)
        self.pack(side=tk.BOTTOM)

    def draw_stats(self, player_stats: tuple[int, int, int]) -> None:
        """Draws the player's stats

        Parameters:
            player_stats: tuple containing player health, hunger and thirst
        """
        for col, stat in enumerate(player_stats):
            self.annotate_position((STAT_ROW, col), str(stat))

    def draw_headings(self) -> None:
        """Draws the headings for each player stat in the window"""
        for col, heading in enumerate(STAT_HEADINGS):
            self.annotate_position((HEADING_ROW, col), heading)

    def draw_coins(self, num_coins: int) -> None:
        """Draws the number of coins the player has in the window"""
        self.annotate_position(COIN_POSITION, str(num_coins))


class InventoryView(tk.Frame):
    """View class that displays player inventory items"""
    def __init__(self, master: Union[tk.Tk, tk.Frame], **kwargs) -> None:
        """Creates an inventory view within the master frame

        Parameters:
            master: the tk frame that encapsulates the entire view
        """
        super().__init__(master, width=INVENTORY_WIDTH)
        self.pack(
            side=tk.RIGHT,
            fill=tk.BOTH,
            expand=tk.TRUE
        )
        self._callback = None

    def set_click_callback(self, callback: Callable[[str], None]) -> None:
        """Sets the function to be called when item label is clicked

        Parameters:
            callback: callable function that applies an item
        """
        self._callback = callback

    def clear(self) -> None:
        """Removes all child widgets from the inventory view"""
        for item_label in self.winfo_children():
            item_label.destroy()

    def _draw_item(self, name: str, num: int, colour: str) -> None:
        """Creates and binds a label for each item type in inventory

        Parameters:
            name: Name of the item
            num: Quantity of the item in the user's inventory
            colour: background colour for the item label
        """
        text = f"{name}: {str(num)}"
        label = tk.Label(
            self,
            text=text,
            bg=colour,
            font=TEXT_FONT
        )

        if self._callback:
            label.bind(
                "<Button-1>",
                lambda event, item_name=name: self._callback(item_name)
            )

        label.pack(
            side=tk.TOP,
            fill=tk.BOTH
        )

    def draw_inventory(self, inventory: Inventory) -> None:
        """Draws all the non-coin inventory labels with their quantities
           and binds a callback for each one.

        Parameters:
            inventory: The player's current inventory
        """
        inv_header = tk.Label(
            self,
            font=HEADING_FONT,
            text='Inventory'
        )
        inv_header.pack(side=tk.TOP)

        inventory = inventory.get_items()

        # Iterates through every item that isn't a coin
        for item in inventory:
            if item != COIN_NAME:
                self._draw_item(
                    item,
                    len(inventory[item]),
                    ENTITY_COLOURS[inventory[item][0].get_id()],
                )


class ControlsFrame(tk.Frame):
    """View class that displays restart and new game buttons, along with the
       game timer. """
    def __init__(self, master: Union[tk.Tk, tk.Frame]) -> None:
        """Sets up the control frame and sets the timer to 0

        Parameters:
            master: the tk frame that encapsulates the entire view
        """

        self._master = master
        super().__init__(master)
        self._seconds = 0
        self._minutes = 0
        self._check_file = None

    def _draw_restart(self) -> None:
        """Draws and packs the restart button in the frame"""
        self._restart_button = tk.Button(
            self,
            text=RESTART_GAME,
        )
        self._restart_button.pack(
            side=tk.LEFT,
            expand=tk.TRUE
        )

    def set_reset_callback(self, callback: Callable) -> None:
        """Sets the command of the reset button

        Parameters:
            callback: callable function that resets the game
        """
        self._restart_button.config(command=callback)

    def set_new_game_callback(self, callback: Callable) -> None:
        """Sets the command of the new game button

        Parameters:
            callback: callable function that prompts the new game window
        """
        self._new_button.config(command=callback)

    def set_get_file(self, callback: Callable[[str], None]) -> None:
        """Sets the check command for the button in the new game window"""
        self._check_file = callback

    def get_file_path(self) -> None:
        """Gets the value in the entry box and calls the check file command"""
        self._check_file(self._file_entry.get())

    def _draw_new(self) -> None:
        """Draws the new game button in the control frame"""
        self._new_button = tk.Button(
            self,
            text=NEW_GAME
        )
        self._new_button.pack(
            side=tk.LEFT,
            expand=tk.TRUE
        )

    def _draw_timer(self) -> None:
        """Draws the timer in the control frame"""
        self._timer_label = tk.Label(
            self,
            text='Timer'
        )

        self._timer_label.pack(
            side=tk.TOP,
            expand=tk.TRUE
        )

        self._timer = tk.Label(
            self,
            text=TIMER.format(self._minutes, self._seconds)
        )
        self._timer.pack(
            side=tk.LEFT,
            expand=tk.TRUE
        )
        self._timer.after(1000, self._refresh_timer)

    def _refresh_timer(self) -> None:
        """Increments the game timer by 1 second"""
        self._seconds += 1
        if self._seconds // 60:
            self._minutes += 1
            self._seconds -= 60

        self._timer.configure(text=TIMER.format(self._minutes, self._seconds))
        self._timer.after(1000, self._refresh_timer)

    def reset_timer(self) -> None:
        """Sets the timer to 0 minutes and 0 seconds"""
        self._seconds = 0
        self._minutes = 0
        self._timer.configure(text=TIMER.format(self._minutes, self._seconds))

    def set_timer(self, time: tuple[int, int]) -> None:
        """Sets the timer to the given time

        Parameters:
            time: tuple containing number of minutes and seconds
        """
        self._minutes, self._seconds = time

    def get_time(self) -> tuple[int, int]:
        """Returns the current time of the timer"""
        return self._minutes, self._seconds

    def draw_toplevel(self) -> None:
        """Draws the top level window for new game functionality"""
        self.window = tk.Toplevel(self._master)
        self.window.geometry(NEW_GAME_WINDOW_SIZE)
        self._title = tk.Label(
            self.window,
            text='Enter a file path',
        )
        self._title.pack(
            side=tk.TOP,
            expand=tk.TRUE,
        )
        self._file_entry = tk.Entry(self.window)
        self._file_entry.pack()

        self._file_path_button = tk.Button(
            self.window,
            text='Enter',
            command=self.get_file_path
        )
        self._file_path_button.pack()

    def draw_not_valid(self) -> None:
        """Draws a messagebox stating the given file path is invalid"""
        messagebox.showerror(
            title='Invalid game path',
            message=NOT_VALID_MESSAGE
        )
        self.window.destroy()

    def draw_non_save(self) -> None:
        """Draws a messagebox stating the given save file is invalid"""
        messagebox.showerror(
            title='Invalid save file',
            message=WRONG_SAVE
        )

    def draw_frame(self) -> None:
        """Draws the control frame, with its buttons and labels"""
        self._draw_restart()
        self._draw_new()
        self._draw_timer()
        self.pack(
            side=tk.BOTTOM,
            fill=tk.BOTH,
            expand=tk.TRUE
        )


class Menu(tk.Menu):
    """View class for menu that inherits from tk.Menu"""
    def __init__(self, master: tk.Tk) -> None:
        """Creates the menu view

        Parameters:
            master: the tk frame that encapsulates the entire view
        """
        super().__init__(master)
        self._save_callback = None
        self._load_callback = None
        self._restart_callback = None

    def set_menu_commands(
            self,
            save_callback: Callable,
            load_callback: Callable,
            restart_callback: Callable,
            quit_callback: Callable
    ) -> None:
        """Sets each command for each button in the menu

        Parameters:
            save_callback: command that saves the game state
            load_callback: command that loads a save game
            restart_callback: command that restarts the current game
            quit_callback: command that quits the game
        """

        self._save_callback = save_callback
        self._load_callback = load_callback
        self._restart_callback = restart_callback
        self._quit_callback = quit_callback

    def _save_dialog(self) -> None:
        """Asks the player where to save the save file"""
        path = filedialog.asksaveasfile(
            title="Save file",
            filetypes=(("txt files", "*.txt"), ("all files", "*.*"))
            )
        # Checks if file picker window was closed
        if path:
            self._save_callback(path.name)

    def _load_dialog(self) -> None:
        """Asks the player the location of the save file"""
        path = filedialog.askopenfilename()
        if path:
            self._load_callback(path)

    def draw_menu(self) -> None:
        """Draws the menu and all the menu commands"""
        SAVE_MESSAGE = 'Save Game'
        LOAD_MESSAGE = 'Load Game'
        RESTART_MESSAGE = 'Restart Game'
        self._file_menu = tk.Menu(self)
        self.add_cascade(
            label='File',
            menu=self._file_menu
        )

        self._save_label = self._file_menu.add_command(
            label=SAVE_MESSAGE,
            command=self._save_dialog
        )

        self._load_label = self._file_menu.add_command(
            label=LOAD_MESSAGE,
            command=self._load_dialog
        )

        self._restart_label = self._file_menu.add_command(
            label=RESTART_MESSAGE,
            command=self._restart_callback
        )
        self._quit_label = self._file_menu.add_command(

            label='Quit',
            command=self._quit_callback
        )


class GraphicalInterface(UserInterface):
    """Class that manages the overall game view and enables event handling. It
    also inherits from UserInterface. """
    def __init__(self, master: tk.Tk) -> None:
        """Creates a new Graphical Interface with a master frame

        Parameters:
            master: the tk frame that encapsulate the entire view
        """
        self._master = master
        self._dimensions = None
        self._level_view = None
        self._stats_view = None
        self._inventory_view = None

        self._master.title('MazeRunner')
        self._drawbanner()

    def _drawbanner(self) -> None:
        """Draws the title banner"""
        title_label = tk.Label(
            self._master,
            font=BANNER_FONT,
            bg=THEME_COLOUR,
            text=BANNER_TEXT,
        )
        title_label.pack(
            fill=tk.BOTH
        )

    def create_interface(self, dimensions: tuple[int, int]) -> None:
        """Creates the level view, inventory view, and stats view components,
        given the dimensions.

        Parameters:
            dimensions: Number of rows and columns in the maze
        """
        if TASK == 1:
            self._level_view = LevelView(
                self._master,
                dimensions,
                (MAZE_WIDTH, MAZE_HEIGHT)
                )
        else:
            self._level_view = ImageLevelView(
                self._master,
                dimensions,
                (MAZE_WIDTH, MAZE_HEIGHT)
                )
            self.controls_frame = ControlsFrame(self._master)
            self.controls_frame.draw_frame()

            self._menu = Menu(self._master)
            self._master.config(menu=self._menu)

        self._stats_view = StatsView(
            self._master,
            STATS_WIDTH,
            bg=THEME_COLOUR
            )
        self._inventory_view = InventoryView(self._master, bg=THEME_COLOUR)

    def clear_all(self) -> None:
        """Clears each major component in the view"""
        self._level_view.clear()
        self._stats_view.clear()
        self._inventory_view.clear()

    def reset_stored_images(self):
        """Removes the stored images in the level view"""
        self._level_view.reset_stored_images()

    def set_maze_dimensions(self, dimensions: tuple[int, int]) -> None:
        """Updates the maze dimensions to the given dimensions

        Parameters:
            dimensions: Number of rows and columns in the maze
        """
        self._level_view.set_dimensions(dimensions)

    def bind_keypress(self, command: Callable[[tk.Event], None]) -> None:
        """Binds the move player command to the general keypress event.

        Parameters:
            command: the move player command
        """
        self._master.bind('<Key>', command)

    def set_inventory_callback(self, callback: Callable[[str], None]) -> None:
        """Sets the apply item to be called when an inventory item is
         clicked.

         Parameters:
             callback: command to apply an item to the player
         """
        self._inventory_view.set_click_callback(callback)

    def set_reset_callback(self, callback: Callable) -> None:
        """Sets the command to reset the game state

        Parameters:
            callback: the reset game command
        """
        self.controls_frame.set_reset_callback(callback)

    def set_new_game_callback(self, callback: Callable) -> None:
        """Sets the command to play a new game

        Parameters:
            callback: the new game command
        """
        self.controls_frame.set_new_game_callback(callback)

    def set_file_path_callback(self, callback: Callable[[str], None]) -> None:
        """Sets the command to get a file path for the new game functionality

        Parameters:
            callback: command that checks the validity of a file path
        """
        self.controls_frame.set_get_file(callback)

    def set_menu_callbacks(
            self,
            save_callback: Callable,
            load_callback: Callable,
            restart_callback: Callable,
            quit_callback: Callable
    ) -> None:
        """Sets each command for each button in the menu

        Parameters:
            save_callback: command that saves the game state
            load_callback: command that loads a save game
            restart_callback: command that restarts the current game
            quit_callback: command that quits the game
        """
        self._menu.set_menu_commands(
            save_callback,
            load_callback,
            restart_callback,
            quit_callback
        )

    def draw_inventory(self, inventory: Inventory) -> None:
        """Draws any non-coin inventory item with their quantities and binds
        the callback for each item.

        Parameters:
            inventory: The player's current inventory
        """
        self._inventory_view.clear()
        self._inventory_view.draw_inventory(inventory)

    def draw(
            self,
            maze: Maze,
            items: dict[tuple[int, int], Item],
            player_position: tuple[int, int],
             inventory: Inventory,
            player_stats: tuple[int, int, int]
    ) -> None:
        """ Clears the view and draws the current game state

        Parameters:
            maze: The current Maze instance
            items: The items on the maze
            player_position: The position of the player
            inventory: The player's current inventory
            player_stats: j
        """
        self.clear_all()
        super(GraphicalInterface, self).draw(
            maze,
            items,
            player_position,
            inventory,
            player_stats
        )

    def _draw_inventory(self, inventory: Inventory) -> None:
        """Draws the non-coin inventory items and the number of coins in the
        stats view.

        Parameters:
            inventory: The player's current inventory
        """
        self.draw_inventory(inventory)
        inv = inventory.get_items()
        num_coins = len(inv[COIN_NAME]) if COIN_NAME in inv else 0

        self._stats_view.draw_coins(num_coins)

    def _draw_level(
            self,
            maze: Maze,
            items: dict[tuple[int, int], Item],
            player_position: tuple[int, int]
    ) -> None:
        """ Draws the maze and all its items.

        Parameters:
            maze: The current maze for the level
            items: Maps locations to the items currently at those locations
            player_position: The current position of the player
        """
        self._level_view.draw(maze.get_tiles(), items, player_position)

    def _draw_player_stats(self, player_stats: tuple[int, int, int]) -> None:
        """ Draws the players stats.

        Parameters:
            player_stats: The player's current (HP, hunger, thirst)
        """
        self._stats_view.draw_headings()
        self._stats_view.draw_stats(player_stats)

    def get_level_view(self) -> LevelView:
        """Returns the instance of LevelView"""
        return self._level_view

    def get_master(self) -> tk.Tk:
        """Returns the master frame"""
        return self._master

    def reset_timer(self):
        """Resets the timer to 0 seconds and 0 minutes"""
        self.controls_frame.reset_timer()

    def draw_toplevel(self):
        """Draws the toplevel window for the new game button"""
        self.controls_frame.draw_toplevel()

    def get_menu(self) -> tk.Menu:
        """Returns the instance of Menu"""
        return self._menu

    def draw_not_valid(self):
        """Draws a messagebox stating the given file path is invalid"""
        self.controls_frame.draw_not_valid()

    def draw_non_save(self):
        """Draws a messagebox stating the given save file is invalid"""
        self.controls_frame.draw_non_save()


class ModelV2(Model):
    """ The extended overall model for a game of MazeRunner."""
    def get_level_num(self) -> int:
        """Returns the current level number"""
        return self._level_num

    def get_num_moves(self) -> int:
        """Returns the current number of moves"""
        return self._num_moves

    def set_level_num(self, level_num: int) -> None:
        """Updates the level number to the given level_num

        Parameters:
            level_num: Level Number
        """
        self._level_num = level_num

    def set_num_moves(self, num_moves: int) -> None:
        """Updates the number of moves made by a player

        Parameters:
            num_moves: number of moves taken by the player
        """
        self._num_moves = num_moves

def read_file(file_name: str) -> dict[str, str]:
    """Returns a dictionary representing the info in the save file

    Parameters:
        file_name: file name of the save file
    """
    info = {}
    save_file = open(file_name, 'r')

    save_text = save_file.read()
    save_file.close()

    # Converts the saved data from a string to a dictionary
    right_pos = save_text.find('>')
    save_text = save_text[1:right_pos]
    save_info = save_text.rsplit(';')

    for line in save_info:
        key, _, value = line.partition(':')
        info[key] = value

    return info


class GraphicalMazeRunner(MazeRunner):
    """Controller class that inherits from MazeRunner and controls the game"""
    def __init__(self, game_file: str, root: tk.Tk) -> None:
        """Sets up the initial game state

        Parameters:
            game_file: path to the game file
            root: the tk frame that encapsulates the entire view
        """
        self._file = game_file
        self._view = GraphicalInterface(root)
        self._model = ModelV2(game_file)

    def _handle_keypress(self, e: tk.Event) -> None:
        """Handles a keypress if the user pressed a valid key

        Parameters:
            e: keypress event by the user
        """
        move = e.char
        if move in MOVE_DELTAS:
            self._model.move_player(MOVE_DELTAS.get(move))

        if self._model.has_won():
            self._end_game(WIN_MESSAGE)
        elif self._model.has_lost():
            self._end_game(LOSS_MESSAGE)
        else:
            if self._model.did_level_up():
                self._set_dimensions()
                if TASK == 2:
                    self._view.reset_stored_images()
            self._redraw()

    def _end_game(self, message: str):
        """Ends the game and displays a win or loss message

        Parameters:
            message: message for the user stating they've won or lost
        """
        messagebox.showinfo(
            self._view.get_master(),
            message=message
        )
        self._view.get_master().quit()

    def _apply_item(self, item_name: str) -> None:
        """Attempts to apply  an item to the player

        Parameters:
            item_name: name of the item to be applied
        """
        item = self._model.get_player_inventory().remove_item(item_name)
        item.apply(self._model.get_player())
        self._redraw()

    def _set_dimensions(self) -> None:
        """Updates the dimensions of the maze"""
        level_dimensions = self._model.get_level().get_dimensions()
        self._view.get_level_view().set_dimensions(level_dimensions)

    def _reset(self) -> None:
        """Resets the game to a new game state"""
        self._view.reset_timer()
        self._model = ModelV2(self._file)
        self._set_dimensions()
        self._view.reset_stored_images()
        self._redraw()

    def _new_game(self) -> None:
        """Creates a window prompting the user for a new game file"""
        self._view.draw_toplevel()
        self._view.set_file_path_callback(self.check_file)

    def check_file(self, file_name: str) -> None:
        """Attempts to load a given file name as a game file

        Parameters:
            file_name: name of the game file
        """
        try:
            self._model = ModelV2(file_name)
            self._file = file_name
            self._reset()
        except (KeyError, FileNotFoundError, IndexError, UnicodeDecodeError):
            self._view.draw_not_valid()

    def _save(self, path: str) -> None:
        """Saves the current games state as a save file at a given path

        Parameters:
            path: given path to the user save file
        """
        with open(self._file, 'r') as file:
            old_info = file.readlines()

        save_file = open(path, 'w')
        self._save_info(save_file)
        save_file.write('\n\n')

        for line in old_info:
            if line[0] != SAVE_TYPES['stats_open']:
                save_file.write(line)

        save_file.close()

    def _save_info(self, save_file) -> None:
        """Saves the game information to the save file

        Parameters:
            save_file: save file
        """
        SAVE_FORMAT = '{}:{};'

        info = {
            'inventory': self._save_inventory(),
            'entities': self._model.get_level().get_items(),
            'player_pos': self._model.get_player().get_position(),
            'stats': self._model.get_player_stats(),
            'level_num': self._model.get_level_num(),
            'num_moves': self._model.get_num_moves(),
            'time': self._view.controls_frame.get_time()
        }

        saved_info = ''

        for key in info:
            saved_info += SAVE_FORMAT.format(key, info[key])

        save_file.write(
            f"{SAVE_TYPES['stats_open']}{saved_info}{SAVE_TYPES['stats_close']}"
        )

    def _save_inventory(self) -> str:
        """Returns a string representing the users current inventory, to
        allow for the inventory to be saved"""
        result = ''

        inventory = self._model.get_player_inventory().get_items()

        for item_type in inventory:
            for item in inventory[item_type]:
                result += f"{repr(item)}{SAVE_TYPES['item_separate']}"

        return result

    def _load(self, file_name: str) -> None:
        """Attempts to load a game save at the given file name

        Parameters:
            file_name: file name for the provided save file
        """
        try:
            self._model = ModelV2(file_name)
        except (KeyError, FileNotFoundError, IndexError, UnicodeDecodeError):
            self._view.draw_non_save()
            return

        self._file = file_name
        self._model = ModelV2(self._file)
        load_info = read_file(file_name)

        self._model.set_level_num(int(load_info['level_num']))
        self._model.set_num_moves(int(load_info['num_moves']))

        stats = tuple(map(int, load_info['stats'][1:-1].split(',')))
        player_pos = tuple(map(int, load_info['player_pos'][1:-1].split(',')))

        self._model.get_player().set_position(player_pos)

        self._load_entities(eval(load_info['entities']))
        self._load_stats(stats)
        self._load_inventory(load_info['inventory'])

        time = tuple(map(int, load_info['time'][1:-1].split(',')))
        self._view.controls_frame.set_timer(time)

        self._set_dimensions()
        self._view.reset_stored_images()
        self._redraw()

    def _load_stats(self, stats: tuple[int]) -> None:
        """Loads the player stats from the save file

        Parameters:
            stats: The (HP, hunger, thirst) of the player
        """
        new_hp, new_hunger, new_thirst = stats
        old_hp, old_hunger, old_thirst = self._model.get_player_stats()

        self._model.get_player().change_health(new_hp - old_hp)
        self._model.get_player().change_hunger(new_hunger - old_hunger)
        self._model.get_player().change_thirst(new_thirst - old_thirst)

    def _load_inventory(self, info: str) -> None:
        """Loads the new inventory from the save file

        Parameters:
            info: inventory information in string form
        """
        # Clear inventory
        for item_list in self._model.get_player_inventory().get_items():
            for _ in range(len(item_list)):
                self._model.get_player_inventory().remove_item(item_list)

        inventory = info.rsplit(SAVE_TYPES['item_separate'])[:-1]

        for item in inventory:
            self._model.get_player_inventory().add_item(eval(item))

    def _load_entities(self, saved_entities: dict[tuple[int, int], Item]) -> None:
        """Loads the entities in the level from the save file

        Parameters:
            saved_entities: tuple mapping position to entity instances
        """
        old_entities = self._model.get_level().get_items()

        for pos in list(old_entities):
            if pos not in saved_entities:
                self._model.get_level().remove_item(pos)

    def _quit(self) -> None:
        """Asks the user whether they want to quit or not"""
        quit_choice = messagebox.askyesno(
            title=None,
            message=QUIT_MESSAGE
        )
        if quit_choice:
            self._view.get_master().quit()

    def play(self) -> None:
        """Causes gameplay to occur. It firstly binds the keypress handler,
        sets the inventory callback and allows the game to begin"""
        dimensions = self._model.get_current_maze().get_dimensions()
        self._view.create_interface(dimensions)
        self._redraw()

        self._view.bind_keypress(self._handle_keypress)
        self._view.set_inventory_callback(self._apply_item)

        if TASK == 2:
            self._view.set_reset_callback(self._reset)
            self._view.set_new_game_callback(self._new_game)
            self._view.set_menu_callbacks(
                self._save,
                self._load,
                self._reset,
                self._quit
            )
            self._view.get_menu().draw_menu()


def play_game(root: tk.Tk) -> None:
    """Constructs the controller instance and causes gameplay ot commence"""
    maze_runner = GraphicalMazeRunner(GAME_FILE, root)
    maze_runner.play()
    root.mainloop()


def main():
    """Constructs a tk instance and calls play_game function"""
    root = tk.Tk()
    play_game(root)


if __name__ == '__main__':
    main()
