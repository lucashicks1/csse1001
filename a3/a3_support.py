import tkinter as tk
from typing import Union

from constants import TEXT_FONT


class AbstractGrid(tk.Canvas):
    """ Support for creation of and annotation on grids. """

    def __init__(
        self,
        master: Union[tk.Tk, tk.Frame],
        dimensions: tuple[int, int],
        size: tuple[int, int],
        **kwargs
    ) -> None:
        """ Constructor for AbstractGrid.

        Parameters:
            master: The master frame for this Canvas.
            dimensions: (#rows, #columns)
            size: (width in pixels, height in pixels)
        """
        super().__init__(
            master,
            width=size[0] + 1,
            height=size[1] + 1,
            highlightthickness=0,
            **kwargs
        )
        self._size = size
        self.set_dimensions(dimensions)
    
    def set_dimensions(self, dimensions: tuple[int, int]) -> None:
        """ Sets the dimensions of the grid.

        Parameters:
            dimensions: (#rows, #columns)
        """
        self._dimensions = dimensions

    def get_cell_size(self) -> tuple[int, int]:
        """ Returns the size of the cells (width, height) in pixels. """
        rows, cols = self._dimensions
        width, height = self._size
        return width // cols, height // rows

    def get_bbox(self, position: tuple[int, int]) -> tuple[int, int, int, int]:
        """ Returns the bounding box of the given (row, col) position.

        Parameters:
            position: The (row, col) cell position.

        Returns:
            Bounding box for this position as (x_min, y_min, x_max, y_max).
        """
        row, col = position
        cell_width, cell_height = self.get_cell_size()
        x_min, y_min = col * cell_width, row * cell_height
        x_max, y_max = x_min + cell_width, y_min + cell_height
        return x_min, y_min, x_max, y_max

    def get_midpoint(self, position: tuple[int, int]) -> tuple[int, int]:
        """ Gets the graphics coordinates for the center of the cell at the
            given (row, col) position.

        Parameters:
            position: The (row, col) cell position.

        Returns:
            The x, y pixel position of the center of the cell.
        """
        row, col = position
        cell_width, cell_height = self.get_cell_size()
        x_pos = col * cell_width + cell_width // 2
        y_pos = row * cell_height + cell_height // 2
        return x_pos, y_pos

    def annotate_position(self, position: tuple[int, int], text: str) -> None:
        """ Annotates the cell at the given (row, col) position with the
            provided text.

        Parameters:
            position: The (row, col) cell position.
            text: The text to draw.
        """
        self.create_text(self.get_midpoint(position), text=text, font=TEXT_FONT)

    def clear(self):
        """ Clears all child widgets off the canvas. """
        self.delete("all")
