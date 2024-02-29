from constants import PLAYER

class UserInterface:
    """ Abstract class providing an interface for any MazeRunner View class. """
    def draw(
        self,
        maze: 'Maze',
        items: dict[tuple[int, int], 'Item'],
        player_position: tuple[int, int],
        inventory: 'Inventory',
        player_stats: tuple[int, int, int]
    ) -> None:
        """ Draws the current game state.
        
        Parameters:
            maze: The current Maze instance
            items: The items on the maze
            player_position: The position of the player
            inventory: The player's current inventory
            player_stats: The (HP, hunger, thirst) of the player
        """
        self._draw_level(maze, items, player_position)
        self._draw_inventory(inventory)
        self._draw_player_stats(player_stats)
    
    def _draw_inventory(self, inventory: 'Inventory') -> None:
        """ Draws the inventory information.
        
        Parameters:
            inventory: The player's current inventory
        """
        raise NotImplementedError
    
    def _draw_player_stats(self, player_stats: tuple[int, int, int]) -> None:
        """ Draws the players stats.
        
        Parameters:
            player_stats: The player's current (HP, hunger, thirst)
        """
        raise NotImplementedError
    
    def _draw_level(
        self,
        maze: 'Maze',
        items: dict[tuple[int, int], 'Item'],
        player_position: tuple[int, int]
    ) -> None:
        """ Draws the maze and all its items.
        
        Parameters:
            maze: The current maze for the level
            items: Maps locations to the items currently at those locations
            player_position: The current position of the player
        """
        raise NotImplementedError

class TextInterface(UserInterface):
    """ A MazeRunner interface that uses ascii to present information. """
    def _draw_level(
        self,
        maze: 'Maze',
        items: dict[tuple[int, int], 'Item'],
        player_position: tuple[int, int]
    ) -> None:
        num_rows, num_cols = maze.get_dimensions()
        for row in range(num_rows):
            row_str = ''
            for col in range(num_cols):
                if (row, col) == player_position:
                    row_str += PLAYER
                elif (row, col) in items:
                    row_str += items.get((row, col)).get_id()
                else:
                    row_str += maze.get_tile((row, col)).get_id()
            print(row_str)
    
    def _draw_inventory(self, inventory: 'Inventory') -> None:
        text = str(inventory) if inventory.get_items() != {} else 'Empty'
        print('---------------\nInventory\n' + text + '\n' + '---------------')
    
    def _draw_player_stats(self, player_stats: tuple[int, int, int]) -> None:
        hp, hunger, thirst = player_stats
        print(f'HP: {hp}\nhunger: {hunger}\nthirst: {thirst}')
