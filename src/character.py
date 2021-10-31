"""
What to NPC and characters do?
- they move from tile to tile seemlessly
- they have a sprite image
- they have an inventory
- they have a direction that they point too
"""
from enum import Enum;
import main


class Direction(Enum):
    NORTH = 1
    EAST = 2 
    SOUTH = 3
    WEST = 4

class Character:
    def __init__(self):
        self.facing = Direction.NORTH
        self.curr_pos = (0, 0)
        self.name = "John Doe"
        self.sprite = None  # Tk image object

        self.stats = {
            "current health": 100,
            "max health": 100,
            "atk": 50,
            "sp atk": 50,
            "def": 50,
            "sp def": 50,
            "speed": 50
        }

        self.dialog = []    # list of tuples ("text", function pointer)

        # inventory object goes here


    def move_tiles(self) -> None:
        pass

    def set_curr_pos(self, x:int, y:int) -> None:
        self.curr_pos = (x, y)

    def get_curr_pos(self) -> tuple:
        return self.curr_pos

    def get_facing_direct(self) -> int:
        return self.facing

    def set_facing_direct(self) -> None:    # TODO this needs to be done
        pass

    def set_name(self, name:str) -> None:
        self.name = name

    def get_name(self) -> str:
        return self.name

    def set_stats(self, new_stat:tuple) -> void:
        #tuple format ("stat name": newNUm)
        self.stats[new_stat(0)] = new_stat(1);

    

if __name__ == "__main__":
    pass