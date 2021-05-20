"""
CSSE1001 Assignment 3
Semester 2, 2020
Student: Nhu Phan 
Student ID: s4397098

Tested in Window and everything works well
Tested on Mac - position of ibis at the end is a bit weird
"""

import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import PIL
from PIL import ImageTk, Image

# DEFINING GLOBAL CONSTANTS
TASK_ONE = '1'
TASK_TWO = '2'

GAME_LEVELS = {
    # dungeon layout: max moves allowed
    "game1.txt": 7,
    "game2.txt": 12,
    "game3.txt": 19,
}

PLAYER = "O"
KEY = "K"
DOOR = "D"
WALL = "#"
MOVE_INCREASE = "M"
SPACE = " "

DIRECTIONS = {
    "W": (-1, 0),
    "S": (1, 0),
    "D": (0, 1),
    "A": (0, -1)
}

WIN_TEXT = "You have won the game with your strength and honour!"
LOSE_TEST = "You have lost all your strength and honour."
LOSE_TEXT = "You have lost all your strength and honour."

class Display:
    """Display of the dungeon."""

    def __init__(self, game_information, dungeon_size):
        """Construct a view of the dungeon.

        Parameters:
            game_information (dict<tuple<int, int>: Entity): Dictionary 
                containing the position and the corresponding Entity
            dungeon_size (int): the width of the dungeon.
        """
        self._game_information = game_information
        self._dungeon_size = dungeon_size


def load_game(filename):
    """Create a 2D array of string representing the dungeon to display.
    
    Parameters:
        filename (str): A string representing the name of the level.

    Returns:
        (list<list<str>>): A 2D array of strings representing the 
            dungeon.
    """
    dungeon_layout = []

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            dungeon_layout.append(list(line))

    return dungeon_layout

class Entity:
    """ 
    An abstract superclass of entities in the game
    """

    _id = "Entity"

    def __init__(self):
        """
        Constructs an entity
        """
        self._collidable = True

    def get_id(self):
        """ 
        Return:
            <str> Entity's ID
        """
        return self._id

    def set_collide(self, collidable):
        """ 
        Sets the collision state for the Entity
        Parameters:
            <bool> True if Entity can be collided with. Otherwise, False
        """
        self._collidable = collidable

    def can_collide(self):
        """
        Return:
            <bool> Whether Entity can be collided with
        """
        return self._collidable

    def __str__(self):
        """
        Return:
            <str> A string representation of Entity
        """
        return f"{self.__class__.__name__}({self._id!r})"

    def __repr__(self):
        """
        Return:
            <str> A string representation of Entity
        """
        return str(self)


class Wall(Entity):
    """ 
    An entitty within the game and a subclass of the class Entity.
    Walls are barriers which stop the player's movements
    """

    _id = WALL
    
    def __init__(self):
        """
        Constructs a wall entity
        """
        super().__init__()
        self.set_collide(False)


class Item(Entity):
    """
    An abstract representation of items (key/trash and moveincrease/banana) within the game
    """
    def on_hit(self, game):
        """ 
        Raise:
            NotImplementedError (because this is an abstract class)
        """
        raise NotImplementedError


class Key(Item):
    """
    A special type of Item that is used to unlock the door"""

    _id = KEY

    def on_hit(self, game):
        """
        This method is claled when the player is in the same position as the Key item
        Key is added to the player's inventory and is removed from the dungeon
        Parameters:
            game (class GameLogic)
        """
        player = game.get_player()
        player.add_item(self)
        game._game_information.pop(player.get_position())

class MoveIncrease(Item):
    """
    A special type of item that can add moves to the player's move count
    """

    _id = MOVE_INCREASE

    def __init__(self, moves=5):
        """
        Parameters:
            <int> moves to be added when the player collides with MoveIncrease item
        """
        super().__init__()
        self._moves = moves

    def on_hit(self, game):
        """
        This method is called when the player is in the same position as the MoveIncrease item
        Moves (default = 5) is added into player's move count
        Parameters:
            game (class GameLogic)
        """
        player = game.get_player()
        player.change_move_count(self._moves)
        game.get_game_information().pop(player.get_position())


class Door(Entity):
    """ 
    A special type of entity that the player/ibis can unlock using a Key item
    """
    _id = DOOR

    def on_hit(self, game):
        """
        This method is called when the player is in the same position as the Door entity.
        Parameters:
            game (class GameLogic)
        """
        player = game.get_player()
        for item in player.get_inventory():
            if item.get_id() == KEY:
                game.set_win(True)
                game.get_game_information().pop(player.get_position())
                return

        print("You don't have the key!")


class Player(Entity):
    """
    Representation of the player/ibis within the game.
    Player is a subclass of Entity."""

    _id = PLAYER

    def __init__(self, move_count):
        """
        Constructs a player a default move count
        """
        super().__init__()
        self._move_count = move_count
        self._inventory = []
        self._position = None

    def set_position(self, position):
        """
        Sets the position of the player
        Parameters:
            tuple <int, int> for the coordinates 
        """
        self._position = position

    def get_position(self):
        """
        Return:
            tuple <int, int> for the player's current position
        """
        return self._position

    def change_move_count(self, number):
        """
        Parameters:
            number (int): number to be added to move count
        """
        self._move_count += number

    def moves_remaining(self):
        """ 
        Return:
            <int> player's current move count
        """
        return self._move_count

    def add_item(self, item):
        """
        Adds item (Item) to inventory
        """
        self._inventory.append(item)

    def get_inventory(self):
        """ 
        Return:
            <list> Item/s in the player's inventory
        """
        return self._inventory

class GameLogic:
    """
    Contains game information and methods for the game
    """
    def __init__(self, dungeon_name="game2.txt"):
        """ 
        Constructor of the GameLogic class
        Parameters:
            dungeon_name (str): The name of the level.
        """
        self._dungeon = load_game(dungeon_name)
        self._dungeon_name = dungeon_name
        self._dungeon_size = len(self._dungeon)
        self._player = Player(GAME_LEVELS[dungeon_name])
        self._game_information = self.init_game_information()
        self._win = False

    def get_positions(self, entity):
        """
        Returns a list of the tuples containing all positions of a given Entity type.
        Parameters:
            entity <str>: the id of an entity
        Returns:
            (list<tuple<int, int>>) a list of tuples representing the position/s of a given entity id
        """
        positions = []
        for row, line in enumerate(self._dungeon):
            for col, char in enumerate(line):
                if char == entity:
                    positions.append((row, col))

        return positions

    def init_game_information(self):
        """
        Sets the player's initial position
        Returns:
            dict{<tuple<int, int>>: entity} a dictionary containing the initial position (dict key) and name (dict value) of the entity in that position.
        """
        player_pos = self.get_positions(PLAYER)[0]
        key_position = self.get_positions(KEY)[0]
        door_position = self.get_positions(DOOR)[0]
        wall_positions = self.get_positions(WALL)
        move_increase_positions = self.get_positions(MOVE_INCREASE)
        
        self._player.set_position(player_pos)

        information = {
            key_position: Key(),
            door_position: Door(),
        }

        for wall in wall_positions:
            information[wall] = Wall()

        for move_increase in move_increase_positions:
            information[move_increase] = MoveIncrease()

        return information

    def get_player(self):
        """
        Creates a player instance
        """
        return self._player

    def get_entity(self, position):
        """ 
        Parameters: 
            position (tuple<int, int>)
        Returns:
            A representation of the entity in the position
        """
        return self._game_information.get(position)

    def get_entity_in_direction(self, direction):
        """ 
        Gets the entity name in the direction
        Parameters:
            <str> 'A', 'S', 'D', 'W' 
        Returns: 
            Name (Representation) of an Entity. If no entity in the direction, return None
        """
        new_position = self.new_position(direction)
        return self.get_entity(new_position)

    def get_game_information(self):
        """ 
        Returns:
            {dict(tuple<int,int>): entity} a dictionary containing the position and corresponding
            entity of the current dungeon.
        """
        return self._game_information

    def get_dungeon_size(self):
        """
        Returns:
            <int> the width of the dungeon size
        """
        return self._dungeon_size

    def move_player(self, direction):
        """
        Updates the player's position
        Parameters:
            <str> 'A', 'S', 'D', 'W' 
        """
        new_pos = self.new_position(direction)
        self.get_player().set_position(new_pos)

    def collision_check(self, direction):
        """
        Check to see if a player can travel in a given direction
        Parameters:
            direction (str): a direction for the player to travel in.

        Returns:
            (bool): False if the player can travel in that direction without colliding otherwise True.
        """
        new_pos = self.new_position(direction)
        entity = self.get_entity(new_pos)
        if entity is not None and not entity.can_collide():
            return True
        
        return not (0 <= new_pos[0] < self._dungeon_size and 0 <= new_pos[1] < self._dungeon_size)

    def new_position(self, direction):
        """ 
        Gets the coordinates of the position in the direction given.
        Parameters:
            <str> 'A', 'S', 'D', 'W' 
        Returns:
            (int, int) a tuple of two integers representing the new position in the given position
        """
        x, y = self.get_player().get_position()
        dx, dy = DIRECTIONS[direction]
        return x + dx, y + dy

    def check_game_over(self):
        """ 
        Checks if game is over.
        Returns:
            <bool> True if player loses (when has no moves left). Otherwise, False.
        """
        return self.get_player().moves_remaining() <= 0

    def set_win(self, win):
        """
        Sets the game's win or lose state
        Parameters:
            <bool> True if win. Otherwise, False.
        """
        self._win = win

    def won(self):
        """
        Return:
            <bool> the game's win state
        """
        return self._win

class AbstractGrid(tk.Canvas):
    def __init__(self,master, rows , cols, width, height, **kwargs):
        """
        Constructs an abstract superclass for the dungeon map
        Parameters:
            master (the main window - root)
            <int> rows
            <int> cols
            <int> width
            <int> height
            
        """
        super().__init__(master)
        self._master = master
        self._rows = rows
        self._cols = cols
        self._width = width
        self._height = height
        self._grid_width = width/cols
        self._grid_height = height/rows
        self._game_canvas = tk.Canvas(self._master,height = self._width, width = self._width,bg='light grey')
        self._game_canvas.pack(side= tk.LEFT, anchor = tk.NW)
        
  
    def get_bbox(self, position):
        """
        Gets the bounding box
        Parameters:
            <tuple> position
        Return:
            <list> of x and y pixel coordinates bounding box of the position
        """
        (x,y) = position
        self._bbox = [self._grid_width*(y), self._grid_height*(x), self._grid_width*(y+1),self._grid_height*(x+1) ]
        return self._bbox

    def pixel_to_position(self, pixel):
        """
        Gets the position of the corresponding pixel coordinates
        Parameters:
            <tuple> pixel coordinates
        Return:
            <tuple> representing the row, column number of the position respectively
        """
        (x,y) = pixel
        row_no = int(x/self._grid_height)
        col_no = int(y/self._grid_width)
        return (row_no, col_no)

    def get_position_centre(self, position):       
        """
        Gets the centre point of the position
        Parameters:
            <tuple> position
        Returns:
            <tuple> of pixel coordinates of centre point
        """
        (x,y) = position
        y_centre_coord = self._height/(self._rows*2) * (2*x+1)
        x_centre_coord = self._width/(self._cols*2) * (2*y+1)
        return (x_centre_coord, y_centre_coord)

    def annotate_position(self, position, text):
        """
        Parameters:
            <tuple> position (NOT PIXEL)
            <str> text to be annotated
        """
        centre_coord = self.get_position_centre(position)
        self._game_canvas.create_text(centre_coord[0],centre_coord[1], fill = 'Black', font = "Arial 12", text =  text)

        
#FOR TASK ONE    
class DungeonMap(AbstractGrid):
    def __init__(self, master, size, width=600, **kwargs):
        """
        Draws grids for task one
        Parameters:
            master (root - main window)
            <int> size of the dungeon depending on game level
            <int> width, default at 600
        """
        super().__init__(master, size, size, width, width, **kwargs)

    def draw_grid(self, dungeon , player_position):
        """
        Draws the dungeon map for task one with grids
        Parameters:
            <dict> dungeon containing the game information; position as key and entity as value
            <tuple> representing the player's current position
        """
        # Clears dungeon before redrawing
        self._game_canvas.delete('all')
        i = 0
        while i < len(dungeon):
            for position in dungeon:
                bbox = self.get_bbox(position)
                entity = str(dungeon[position])
                if "MoveIncrease" in entity:
                    self._game_canvas.create_rectangle(bbox[0], bbox[1], bbox[2], \
                                                       bbox[3], fill ='orange')
                    self.annotate_position(position, 'Banana')

                elif "Door" in entity:
                    self._game_canvas.create_rectangle(bbox[0], bbox[1], bbox[2], \
                                                       bbox[3], fill ='dark red')
                    self.annotate_position(position, 'Nest')

                elif "Wall" in entity:
                    self._game_canvas.create_rectangle(bbox[0], bbox[1], bbox[2], \
                                                       bbox[3], fill ='grey')

                elif "Key" in entity:
                    self._game_canvas.create_rectangle(bbox[0], bbox[1], bbox[2], \
                                                       bbox[3], fill ='yellow')
                    self.annotate_position(position, 'Trash')

                i+=1

            player_bbox =self.get_bbox(player_position)
            self._game_canvas.create_rectangle(player_bbox[0], player_bbox[1], player_bbox[2], \
                                                player_bbox[3], fill ='light green')
            self.annotate_position(player_position, 'Ibis')

#FOR TASK TWO        
class AdvancedDungeonMap(AbstractGrid):
    def __init__(self, master, size, width=600, **kwargs):
        """
        Draw dungeon map for task two
        Parameters:
            master (root - main window)
            <int> size of dungeo
            <int> width, default at 600
        """
        super().__init__(master, size, size, width,width, **kwargs)


    def load_images(self, filename, size):
        """
        Loads and resize the image
        Parameters:
            <str> the filename of the image
            <int> size to be loaded and resized
        """
        image = Image.open(filename)
        image = image.resize((size, size), Image.ANTIALIAS)
        return ImageTk.PhotoImage(image)

    def draw_advanced_grid(self, dungeon , player_position):
        """
        Draws the dungeon maps of entities
        Parameters:
            <dict> dungeon containing the game information; position as key and entity as value
            <tuple> representing the player's current position
        """
        # Loads image
        self._game_board_img = {
            "key": self.load_images("images/key.png", int(self._grid_width)),
            "space": self.load_images("images/empty.png", int(self._grid_width)),
            "moveincrease": self.load_images("images/moveIncrease.png", int(self._grid_width)),
            "player": self.load_images("images/player.png", int(self._grid_width)),
            "wall": self.load_images("images/wall.png", int(self._grid_width)),
            "door": self.load_images("images/door.png", int(self._grid_width))
            }
        # Clears dungeon map before redrawing
        self._game_canvas.delete('all')
        
        for row in range(len(dungeon)):
            # Draws the grasses
            for col in range(len(dungeon)):
                grass_centre = self.get_position_centre((row, col))
                self._game_canvas.create_image(grass_centre[0], grass_centre[1], image = self._game_board_img["space"])
    
        i = 0
        while i < len(dungeon):
            for key in dungeon:
                self._position = key   # key is the tuple (row, col) of  the entities in the game
                centre_position = self.get_position_centre(self._position)

                str_entity = str(dungeon[key])
                if "MoveIncrease" in str_entity:
                    self._game_canvas.create_image(centre_position[0], centre_position[1], image = self._game_board_img["moveincrease"])

                elif "Door" in str_entity:
                    self._game_canvas.create_image(centre_position[0], centre_position[1], image = self._game_board_img["door"])

                elif "Wall" in str_entity:
                    self._game_canvas.create_image(centre_position[0], centre_position[1], image = self._game_board_img["wall"])

                elif "Key" in str_entity: 
                    self._game_canvas.create_image(centre_position[0], centre_position[1],image = self._game_board_img["key"])
                    
                i+=1

            player_centre = self.get_position_centre(player_position)
            self._game_canvas.create_image(player_centre[0], player_centre[1], image = self._game_board_img["player"])
     

class KeyPad(AbstractGrid):
    def __init__(self, master, width =200, height = 100, **kwargs):
        """
        Creates the keypad for user interaction and clicks
        Parameters:
            master (main - root window)
            <int> width, default at 200
            <int> height, default at 100
        """
        self._width = width
        self._height = height
        self._grid_width = width/3
        self._grid_height = height/2
        self._cols = 3
        self._rows = 2
        self._keypad_canvas = tk.Canvas(master, width = 200, height =100)
        self._keypad_canvas.pack(side= tk.LEFT,anchor = tk.W)
 
    def draw_keypad(self):
        """
        Draws the keypad
        """
        
        _key_position = {"N": (0,1),
                        "S": (1,1),
                        "E": (1,2),
                        "W": (1,0),
                        }
        
        for key in _key_position:
            bbox = self.get_bbox(_key_position[key])
            centre = self.get_position_centre(_key_position[key])
            self._keypad_canvas.create_rectangle(bbox[0], bbox[1], bbox[2], bbox[3], fill = 'grey')
            self._keypad_canvas.create_text(centre[0], centre[1], fill = 'Black',font ='Arial 10', text=key)
    
    def pixel_to_direction(self, pixel):   
        """
        Converts the x,y pixel position to the direction of the arrow depicted at that position
        Returns:
            (tuple<int,int>) position to the direction
        """
        (x,y) = pixel     # Coordinates clicked at
        _bbox = {"W": self.get_bbox((0,1)),
        "S": self.get_bbox((1,1)),
        "D": self.get_bbox((1,2)),
        "A": self.get_bbox((1,0)),
        }

        for key in _bbox:
            if x <= _bbox[key][2] and x >= _bbox[key][0] and y <= _bbox[key][3] and y >= _bbox[key][1]:
                return (DIRECTIONS[key])

class StatusBar(tk.Frame):
    def __init__(self, master, width = 620, height = 200,**kwargs):
        """
        Constructs a status bar, containing new game/quit buttons, timer, and number of moves remaining
        on the bottom of the dungeon map
        Parameters:
            master (root - main window)
            <int> width, default is 620
            <int> height, default is 200
            ***kwargs
                game: reference to GameApp 
        """
        super().__init__(master)
        self._master = master
        self.pack(side = tk.LEFT, anchor=tk.NW, expand = True )

        # Get the game instance and the number of moves remaining
        self._game = kwargs["game"] 
        self._moves = self._game._ibis.moves_remaining()  

        # New Game / Quit Buttons
        self._button = Canvas(self, border='1')
        self._button.pack(side=tk.LEFT, fill= tk.BOTH, expand =1) 
        new_game = Button(self._button, text = 'New Game', command = self.new_game_command )
        new_game.pack(anchor=tk.N, pady='10',padx='30', expand ='1')
        quit_button = Button(self._button, text = 'Quit', command = self.quit_command)
        quit_button.pack(anchor=tk.S, padx='30',expand ='1')

        # Timer
        self._time = tk.StringVar()
        self._time.set("0 m 0 s")
        photo = (Image.open("images/clock.png")).resize((int(40),int(50)), Image.ANTIALIAS)
        clock = ImageTk.PhotoImage(photo)  
        self._hourglass_image = Label(self)
        self._hourglass_image.image = clock
        self._hourglass_image.configure(image=clock)
        self._hourglass_image.pack(side = tk.LEFT, padx =(100,0))
        
        self._text_frame = tk.Frame(self)
        self._time_label = Label(self._text_frame, text = 'Time Elapsed', font = "Arial 12")
        self._time_label.pack()
        self._time_elapsed = Label(self._text_frame, textvariable = self._time)
        self._time_elapsed.pack()
        self._text_frame.pack(side = tk.LEFT)
        
        # Start the timer when the class is instantiated
        self._seconds = 0
        self._minutes = 0
        self._time_elapsed.after (1000, self.update_timer)
    
        # Moves Display
        self._moves_left = tk.StringVar()
        self._moves_left.set(str(self._moves) + " moves removing")
        photo_two = (Image.open("images/lightning.png")).resize((int(40),int(50)), Image.ANTIALIAS)
        lightning = ImageTk.PhotoImage(photo_two)   
        self._hourglass_image = Label(self)
        self._hourglass_image.image = lightning
        self._hourglass_image.configure(image=lightning)
        self._hourglass_image.pack(side = tk.LEFT, padx = (100,0))

        self._move_frame = tk.Frame(self)  
        self._moves_label = Label(self._move_frame, text ="Moves left", font = 'Arial 12')
        self._moves_label.pack()
        self._moves_remaining = Label(self._move_frame, textvariable = self._moves_left ) 
        self._moves_remaining.pack()
        self._move_frame.pack(side = tk.RIGHT)
        
    def update_timer(self):
        """ 
        Updates the timer every second
        """
        self._seconds +=1
        self._time.set(f"{self._minutes} m {self._seconds} s")
        if self._seconds == 60:
            self._minutes +=1
            self._seconds = 0
            self._time.set(f"{self._minutes} m {self._seconds} s")
        self._time_elapsed.after(1000, self.update_timer)

    def set_time(self, minute, second):
        """
        Set the timer to start at a particular time
        Parameters:
            <int> minute
            <int> second
        """
        self._minutes = minute
        self._seconds = second

    def get_time(self):
        """
        Gets the current time on timer
        Returns:
            <int> (tuple<mins, secs>) 
        """
        return (self._minutes, self._seconds)

    def update_moves(self):
        """
        Updates the moves remaining
        """
        moves = str(self._game._ibis.moves_remaining())
        self._moves_left.set(f"{str(moves)} moves remaining")

    def new_game_command(self):
        """
        Calls the new_game method in GameApp to start a new game
        """
        self._game.new_game()

    def quit_command(self):
        """
        Calls the quit_game method in GameApp to quit the game
        """
        self._game.quit_game()

    def time_reset(self):
        """
        Resets the time
        """
        self._time.set("0 m 0 s")
        self._seconds = 0
        self._minutes = 0
        
    def move_reset(self):
        """
        Resets the number of moves to the initial number of moves (depending on game levels)
        """
        self._moves = self._game._dungeon_size
        self._moves_left.set(f"{str(self._moves)} moves remaining")
        
class GameApp():
    """
    Controller class, manages the necessary communication between view and model classes and handles events
    """
    def __init__(self, master, task = TASK_ONE, dungeon_name ='game2.txt'):
        """
        Initialise and set class variables
        Parameters:
            master (root - main window)
            <str> indicates what task for run, '1' if task one or '2' if task two
            <str> name of the dungeon, default is game2
        """
        self._master = master
        self._game_frame = tk.Frame(self._master)
        self._game_frame.pack(anchor = tk.W)
        self._game = GameLogic()
        self._dungeon_name = dungeon_name
        self._dungeon_size = self._game._dungeon_size
        self._ibis = self._game.get_player()
        self._initial_position = self._ibis.get_position()
        self._master.bind("<Key>", self.key_pressed)
        
        # File menu
        self._task = task
        if self._task == TASK_TWO:
            file_bar = tk.Menu(master)
            master.config(menu = file_bar)
            file_menu = tk.Menu(file_bar)
            file_bar.add_cascade(label = "File", menu = file_menu)
            file_menu.add_command(label="Save game", command = self.save_game)
            file_menu.add_command(label="Load game", command = self.load_game)
            file_menu.add_command(label="New game", command = self.new_game)
            file_menu.add_command(label="Quit game", command = self.quit_game)

        # Draw the dungeon map and the keypad
        self.init_board()
        self.draw_key()
   
    def init_board(self):
        """
        Draws the initial dungeon map
        """
        if self._task == TASK_ONE:
            self._canvas = DungeonMap(self._game_frame, self._dungeon_size)
            self._canvas.draw_grid(self._game._game_information, self._ibis.get_position())
            
        elif self._task == TASK_TWO:
            self._canvas = AdvancedDungeonMap(self._game_frame, self._dungeon_size)
            self._canvas.draw_advanced_grid(self._game._game_information, self._ibis.get_position())
            self._status_bar = StatusBar(self._master,self._dungeon_size, game = self)
    
    def draw_key(self):
        """
        Draws the keypad
        """
        self._keypad = KeyPad(self._game_frame)
        self._keypad.draw_keypad()
        self._keypad._keypad_canvas.bind("<Button-1>", self.mouse_clicked)

    def quit_game(self):
        """
        This method is called when the player presses the quit game button or from the file menu
        Closes main (root) window is player confirms 'Yes'.
        """
        quit_box = messagebox.askquestion(type=messagebox.YESNO,
            title="Quit",
            message="Are you sure you want to quit?")
        if quit_box == messagebox.YES:
            self._master.destroy()

    def new_game(self):
        """
        This method is called when the player presses the new game button from the file menu
        Resets all necessary variables for a new game, including time, moves, position, etc.
        """
        for widget in self._game_frame.winfo_children():
            widget.destroy()
        # Get a new instance of GameLogic, Player, AdvancedDungeonMap class
        self._game = GameLogic()
        self._ibis = self._game.get_player()    
        self._canvas = AdvancedDungeonMap(self._game_frame, self._dungeon_size)
        self._canvas.draw_advanced_grid(self._game.init_game_information(), self._initial_position)
        self.draw_key()
        self._status_bar.time_reset()
        self._status_bar.move_reset()
        self._status_bar.update_moves()

    def save_game (self):
        """
        Saves the game to a text file.
        """
        text = ""
        _game_information = self._game._game_information

        # Writes True into text file if Item in dungeon. Otherwise, False
        _entities = [KEY, MOVE_INCREASE]
        for entity in _entities:
            if _game_information.get(self._game.get_positions(entity)[0]) != None:
                text+= "True\n"
            else: 
                text+= "False\n"
        # Writes player's current position
        text+=(str(self._ibis.get_position()) + "\n" )

        # Writes other necessary game info
        text += str(self._game._dungeon_name + "\n") 
        text += str(self._status_bar.get_time()[0]) + "\n"
        text += str(self._status_bar.get_time()[1])+ "\n"
        text+= str(self._ibis.moves_remaining())
        filename = filedialog.asksaveasfilename(defaultextension=".txt", title = 'Save')
        
        file_saved = open(filename + '.txt', 'w')
        file_saved.write(text)
        file_saved.close()

    def load_game(self):
        """
        Loads a text file and uses data in text file to set the variables necessary to continue the saved game.
        If error occurs, a message box will pop up.
        """
        try:
            filename = filedialog.askopenfilename(filetypes=[('Text files', '*.txt')], title = 'Load Game')
            if filename:
                game_loaded = open(filename, 'r')
                text = game_loaded.read()
                text = text.splitlines()
                game_loaded.close()
                
                # Create a new instance of game, with the saved dungeon_size
                self._game = GameLogic(text[3])
                self._ibis = self._game.get_player()
                self._ibis.set_position((int(text[2][1]),int(text[2][4]))) 
                
                # Get the saved data of games
                _dungeon_size = (self._game.get_dungeon_size())
                _seconds = int(text[5])
                _minutes = int(text[4])
                self._ibis._move_count = int(text[6])
                self._status_bar.set_time(_minutes, _seconds)
                self._status_bar.update_moves()

                # If the key and/or move increase item was obtained in the saved game,
                # pop from game information dictionary and add key to inventory
                if text[0] == "False": 
                    self._game._game_information.pop(self._game.get_positions(KEY)[0])
                    self._ibis.add_item(Key())
                    
                if text[1] == "False":
                    self._game._game_information.pop(self._game.get_positions(MOVE_INCREASE)[0])


                # If changing from a different game level, need to initialise the board sizes, rows, cols
                self._canvas._cols = _dungeon_size
                self._canvas._rows = _dungeon_size
                self._canvas._grid_width = self._canvas._width/self._canvas._cols
                self._canvas.draw_advanced_grid(self._game._game_information, self._ibis.get_position())

        except:
            load_wrongfile = messagebox.showinfo("Error", "You've tried to load an invalid game file. \
                                                 Please ensure file is .txt and contains all necessary information.")
            
    def key_pressed (self, event):
        """
        Stores the key pressed into a variable
        Parameters: 
            <event object>: key pressed by user on keyboard
        """
        letter =str((event.char)).upper()
        self.play(letter)
        
    def mouse_clicked(self, event):
        """
        Converts the position of where the mouse was clicked to a <str> letter
        'A', 'S', 'D' or 'W' representing the direction
        Parameters: 
            <event object>: key pressed by user on keyboard
        """
        letter = None   #local variable
        self._direction=self._keypad.pixel_to_direction((event.x, event.y))
        for key, value in DIRECTIONS.items():
            if value == self._direction:
                letter = key 
        self.play(letter)
    
        
    def play(self, direction_letter):
        """
        Draws the dungeon, moves the ibis, updates the status bar
        and checks if game status is win
        Parameters:
            <str> a letter representing direction to move the ibis.
            Note that ibis will only be moved with direction_letter
            is in ['A', 'S', 'D', 'W']
        """

        self._letter_direction = direction_letter
        self._ibis_pos = self._ibis.get_position()
        
        # Check if direction is valid. If yes, moves minus 1
        if self._letter_direction in DIRECTIONS.keys():
            self._ibis.change_move_count(-1)
            
            if self._task == TASK_TWO:
                self._status_bar.update_moves()

            # Checks if wall is in the direction
            if not self._game.collision_check(self._letter_direction):
                self._ibis.set_position((self._ibis_pos[0]+DIRECTIONS[self._letter_direction][0], self._ibis_pos[1]+DIRECTIONS[self._letter_direction][1]))

                _entity = self._game.get_entity(self._ibis.get_position())
                if _entity is not None:
                    _entity.on_hit(self._game)
                    
                if self._task == TASK_ONE:
                    self._canvas.draw_grid(self._game._game_information, self._ibis.get_position())
                    
                elif self._task == TASK_TWO:
                    self._canvas.draw_advanced_grid(self._game._game_information, self._ibis.get_position())
                    self._minutes= self._status_bar._minutes
                    self._seconds = self._status_bar._seconds
                    self._status_bar.update_moves()

        # Check if game status is win/lose 
        if self._game.won() == True:
          
            if self._task == TASK_ONE:
                tk.messagebox.showinfo(title='You Won', message=WIN_TEXT)
                
            elif self._task == TASK_TWO:
                end_game = messagebox.askquestion(type=messagebox.YESNO, title="You Won!",
                                                  message = f"You have finished the level with a score of {self._minutes* 60 + self._seconds}.\
                                                    \n Would you like to play again?")
                if end_game == messagebox.NO:
                    self._master.destroy()
                elif end_game == messagebox.YES:
                    self.new_game()

        elif self._ibis.moves_remaining() == 0 and self._game.won()==False:
            if self._task == TASK_ONE:
                tk.messagebox.showinfo(title='You lose', message=LOSE_TEXT)
                
            elif self._task == TASK_TWO:
                end_game = messagebox.askquestion(type=messagebox.YESNO, title="You Lose!",
                                                  message = f"Would you like to play again?")
                if end_game == messagebox.NO:
                    self._master.destroy()
                elif end_game == messagebox.YES:
                    self.new_game()

def main():
    """
    Game window and title are created and GameApp is initialised
    """
    root = tk.Tk()
    root.title('Key Cave Adventure Game')
    game_title = tk.Frame(root)
    game_title.pack(fill=tk.X)
    title_label = tk.Label(game_title, text = 'Key Cave Adventure Game', bg='light green', font='Times 30')
    title_label.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)

    # UNCOMMENT THE TASK TO RUN AND COMMENT THE OTHER
    game = GameApp(root)
    #game = GameApp(root, TASK_TWO )
    
    root.mainloop()


if __name__ == "__main__":
    main()
