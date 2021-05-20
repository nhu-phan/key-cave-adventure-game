"""
CSSE1001 Assignment 2
Semester 2, 2020
"""
from a2_support import *

__author__ = "Nhu Phan"

class GameLogic:
    """
    Contains game information and methods for the game
    """
    def __init__(self, dungeon_name="game1.txt"):
        """Constructor of the GameLogic class.

        Parameters:
            dungeon_name (str): The name of the level.
        """
        self._dungeon = load_game(dungeon_name)
        self._dungeon_name = dungeon_name
        self._dungeon_size = len(self._dungeon)
        self._player = Player(GAME_LEVELS[dungeon_name])
        self._game_information = self.init_game_information()
        self._upward = None
        self._entity_in_direction = None
        self._win = False
        self._player_init_position = None
        self._set_initial_position = None

    def get_positions(self, entity):
        """ Returns a list of tuples containing all positions of a given Entity
             type.

        Parameters:
            entity (str): the id of an entity.

        Returns:
            (list<tuple<int, int>>): Returns a list of tuples representing the 
            positions of a given entity id.
        """
        positions = []
        for row, line in enumerate(self._dungeon):
            for col, char in enumerate(line):
                if char == entity:
                    positions.append((row,col))

        return positions

    def get_dungeon_size (self):
        """
        Return:
            (int) The width of the dungeon
        """
        return self._dungeon_size

    def init_game_information (self):
        """
        Sets the player's initial position

        Return:
            dict<tuple<int,int>: entity> A dictionary of containing the ititial
            position (dict key) and name (dict value) of entity in that position.
        """
        self._game_information = {}
        for index in self.get_positions(KEY):
            self._game_information[index] = Key()

        for index in self.get_positions(DOOR):
            self._game_information[index] = Door()
            
        for index in self.get_positions(WALL):
            self._game_information[index] = Wall()

        for index in self.get_positions(MOVE_INCREASE):
            self._game_information[index] = MoveIncrease()

        # sets the player's initial position
        self._player_init_position = self.get_positions(PLAYER)
        self._set_init_position = self._player.set_position((self._player_init_position[0]))
        
        return self._game_information

    def get_player(self):
        """
        Creates a player instance
        """
        return self._player

    def get_entity (self, position):
        """
        Parameters: position (tuple<int,int>)

        Return:
            Representation of the entity in the position.
        """
        return self._game_information.get(position)  

    def get_entity_in_direction(self, direction:str):
        """
        Gets the entity name in the direction.
        
        Parameters:
            'A', 'S', 'D' or 'W' (str)
        
        Return:
            Name (Representation) of an Entity. If no entity in the direction, return None.
        """
        # gets the current position of the player
        (num1, num2) = self.get_player().get_position()
        if direction == 'W':
            self._entity_in_direction = self._game_information.get(((num1-1), num2)) 
            return self._entity_in_direction
            
        elif direction == 'S':
            self._entity_in_direction = self._game_information.get(((num1+1), num2))
            return self._entity_in_direction
            
        elif direction == 'D':
            self._entity_in_direction = self._game_information.get((num1, (num2+1)))
            return self._entity_in_direction
        
        elif direction == 'A':
            self._entity_in_direction = self._game_information.get((num1, (num2-1)))
            return self._entity_in_direction

    def get_game_information (self):
        """
        Return:
            dict<tuple<int, int>: entity> A dictionary containing the position
            and corresponding entity of the current dungeon.
        """

        for index in self.get_positions(KEY):
            self._game_information[index] = Key()

        for index in self.get_positions(DOOR):
            self._game_information[index] = Door()
            
        for index in self.get_positions(WALL):
            self._game_information[index] = Wall()

        for index in self.get_positions(MOVE_INCREASE):
            self._game_information[index] = MoveIncrease()

        return self._game_information        

    def collision_check (self, direction:str):
        """
        Checks whether if the player can travel in the given direction.

        Parameters:
            'A', 'S', 'D' or 'W' (str)
            
        Return:
            (bool) Returns whether the player can travel in the given
            direction. If True, player cannot travel in that direction.
            Otherwise, False.
        """
        entity_in_direction = str(self.get_entity_in_direction(direction))
        if entity_in_direction == "Wall('#')":
            return True
        return False

    def new_position(self, direction:str):
        """
        Checks the coordinates of the position in the direction given.

        Parameters:
            'A', 'S', 'D' or 'W' (str)
            
        Return:
            (int, int) A tuple of two integers that represents the new position in the given position.
        """
        self._position = self.get_player().get_position() 
        
        
        (num1, num2) = self._position
        if direction == 'W':
            self._position = (num1-1, num2)
            return self._position
            
        elif direction == 'S':
            self._position = (num1+1, num2)
            return self._position
            
        elif direction == 'D':
            self._position = (num1, num2+1)
            return self._position
        
        elif direction == 'A':
            self._position = (num1, num2-1)
            return self._position

    def move_player(self, direction: str):
        """
        Updates the player's position to place them one position in the given direction.

        Parameters:
            'W', 'D', 'A', 'S' <str>

        """
        # updates the Player class, get_position method
        self._position = self._player.get_position()
        (x,y) = self._position

        if direction == 'W':   
            self._position = self._player.set_position((x-1, y))
    
        elif direction == 'S':
            self._position = self._player.set_position((x+1, y))

        elif direction == 'D':
            self._position = self._player.set_position((x, y+1))

        elif direction == 'A': 
            self._position = self._player.set_position((x, (y-1)))


    def check_game_over(self):
        """
        Checks if game is over.

        Return:
            (bool) True if player loses (when player has no more moves left).
            Otherwise, False.
        """
        if self.get_player()._move_count <= 0:
            return True
        return False

    def set_win(self, win: bool):
        """
        Sets the game's win or lose state.
        
        Parameters:
            (bool) True if win. Otherwise, False.
        """
        self._win = win

    def won(self):
        """
        Return:
            (bool) The game's win state.
        """
        return self._win



class Entity:
    """
    A superclass of entities in the game
    """
    def __init__(self):
        """
        Constructs an entity
        """
        self._collidable = True
        self._id = 'Entity'
        self._rep = None
        self._class_name = __class__.__name__

    def get_id (self):
        """
        Return:
            <str> Entity's ID 
        """
        return self._id

    def set_collide (self, collidable: True):
        """
        Sets the collision state for the Entity.
        
        Parameters:
            (bool) True is Entity can be collided with. Otherwise, False
        """
        self._collidable = collidable

    def can_collide (self):
        """
        Return:
            (bool) Whether Entity can be collided with
        """
        
        if str(self._collidable) == "False":
            return False
        return True

    def __str__(self):
        """
        Return:
            (str)  A string representation of Entity
        """
        return f"{self._class_name}('{self._id}')"
    
    def __repr__(self):
        """
        Return:
            (str)  A string representation of Entity
        """
        return f"{self._class_name}('{self._id}')"

class Wall (Entity):
    """
    An entity within the game and a subclass of the class Entity.
    Walls are barriers which stop the Player's movements.
    """
    def __init__(self):
        """
        Construct a wall entity
        """
        super().__init__()
        super()
        self._collidable = False
        self._id = WALL
        self._class_name = __class__.__name__

class Door(Entity):
    """
    A special type of entity that player can unlock using a Key item
    """
    def __init__(self):
        """
        Constructs a door entity
        """
        super()
        super().__init__()
        self._id = DOOR
        self._class_name = __class__.__name__

    def on_hit(self, game):
        """
        This method is called when the player is in the same position
        as the Door entity.

        Parameters:
            game (class GameLogic)
        """
        player_position = game.get_player().get_position()
            # gets current position of player
        entity_in_position = str(game.get_entity(player_position))
        if entity_in_position == "Door('D')":
            if game.get_positions(KEY)[0] in game._game_information:
                # if player does not have key in inventory
                print ("You don't have the key!")
            else:
                game.set_win(True)
                game._game_information.pop(player_position)
                
class Item(Entity):
    """
    Abstract representation of items (key and moveincrease within the game.
    """
    def __init__(self):
        """
        Constructs an abstract Item
        """
        super().__init__()
        super()
        self._class_name = __class__.__name__

    def on_hit (self, game):
        """
        Raise:
            NotImplementedError
        """
        # because this is an abstract class
        raise NotImplementedError

class Player(Entity):
    """
    Representation of player within the game.
    Player is a subclass of Entity.
    """
    def __init__(self, move_count):
        """
        Constructs a player with a default move count 
        """
        super().__init__()
        super()
        self._id = PLAYER
        self._class_name = __class__.__name__
        self._move_count = move_count
        self._position = None
        self._collidable = True
        self._inventory = []

    def set_position(self, position):
        """
        Sets the position of the player.

        Parameters:
            tuple <int, int> for the the coordinates of the dungeon.
        """
        self._position = position

    def get_position(self):
        """
        Return:
            <tuple(int, int)> The player's current position
        """
        return self._position

    def change_move_count(self, number):
        # method called when player loses a move or obtained MoveIncrease
        """
        Changes the player's move count

        Parameters:
            (int) integer (positive or negative)
            Positive when move is gained. Else, move is lost.
        """
        self._move_count+= number

    def moves_remaining(self):
        """
        Return:
            (int) Player's current move_count
        """
        return self._move_count
    
    def add_item (self, item):
        """
        Adds item to Player's inventory

        Parameters:
            instance of Item subclasses, being Key() or MoveIncrease(). 
        """
        self._inventory.append(item)
    
    def get_inventory(self):
        """
        Return:
            (list) Item/s in the player's inventory.
        """
        return self._inventory

class Key(Item):
    """
    A special type of Item that is used to unlock the door
    """
    def __init__(self):
        """
        Inherits the __init__() and methods from superclass Item
        """
        super().__init__()
        super()
        self._id = KEY
        self._class_name = __class__.__name__
        self._key_collected = None
        
    def on_hit(self, game):
        """
        This method is called when the player is in the same position
        as the Key item.
        
        Key is added into the player's inventory and is removed from
        the dungeon.

        Parameters:
            game (class GameLogic)
        """
        player_position = game.get_player().get_position()
            # gets current position of player
        entity_in_position = game.get_entity(player_position)
        if str(entity_in_position) == "Key('K')":
            # if entity in the player's position is KEY
            self._key_collected = game.get_entity(player_position)
            game.get_player()._inventory.append(self._key_collected)
            game._game_information.pop(player_position)

class MoveIncrease (Item):
    """
    A special type of item that can add moves to the player's move count
    """
    def __init__(self, moves = 5):
        """
        Inherits the __init__() and methods from superclass Item

        Parameters:
            (int) moves to be added when the player collides with MoveIncrease
            item
        """
        super().__init__()
        super()
        self._moves = moves
        self._id = MOVE_INCREASE
        self._class_name = __class__.__name__
        
    def on_hit(self, game):
        """
        This method is called when the player is in the same position
        as the MoveIncrease item.
        Moves (default = 5) is added into player's move_count

        Parameters:
            game (class GameLogic)
        """
        player_position = game.get_player().get_position()
        # gets current position of player
        entity_in_position = str(game.get_entity(player_position))
        player = game.get_player()
        if entity_in_position == "MoveIncrease('M')":
            player.change_move_count(self._moves)
            game._game_information.pop(player_position)

            
        
class GameApp:
    """
    Acts as a communicator between GameLogic and Display
    """
    def __init__(self):
        """
        Constructor of the GameApp class.
        """
        # creates an instance of GameLogic
        self._plays = GameLogic()    
        self._display = None
        self._player = self._plays.get_player()
        self._player_position = self._player.get_position()
        self._game_information = self._plays._game_information
        self._dungeon_name = self._plays._dungeon_name
        self._dungeon_size = self._plays._dungeon_size

    def draw(self):
        """
        Displays the dungeon with all Entities in their positions
        and player's remainining move count.
        """
        self._display = Display(self._game_information, self._dungeon_size).display_game(self._player.get_position()) 
        print (f"Moves left: {self._player._move_count}\n")

    def play(self):
        """
        Handles player's interaction
        """
        # asking for input only if the game's win state is False
        while self._plays.won() == False:

                # when player loses all moves, while loop breaks
                if self._player._move_count == 0:
                    break
                self.draw()
                player_input = input('Please input an action: ')
                
                if player_input == HELP:
                    print(HELP_MESSAGE)
                    self.draw()
                    player_input = input('Please input an action: ')
                    
                if player_input == QUIT:
                    quit_input = input("Are you sure you want to quit? (y/n): ")
                    if quit_input == 'y':
                        return     
                    else:
                        continue

                #player can investigate the entity
                if INVESTIGATE in player_input:
                    direction = player_input.split()[1]
                    if direction not in VALID_ACTIONS:
                        print(INVALID)
                        continue
                    
                    elif direction in ['A', 'S', 'D', 'W']:
                        self._plays.get_entity_in_direction(direction)
                        message = (f"{self._plays.get_entity_in_direction(direction)} is on the {direction} side.")
                        self._player.change_move_count(-1)
                    print (message)
                    continue
                
                if player_input not in VALID_ACTIONS:
                    print(INVALID)
                    continue

                # checks if player can collide. If yes, reduce move count by one and move player
                if self._plays.collision_check(player_input) == True:
                    print(INVALID)
                    self._player.change_move_count(-1)
                    continue

                self._plays.move_player(player_input)
                # checks if item collided is Key, MoveIncrease or Door and call Entity.on_hit()
                Key().on_hit(self._plays)
                if str(self._dungeon_name) != 'game1.txt':
                    MoveIncrease().on_hit(self._plays)
                Door().on_hit(self._plays)
                self._player.change_move_count(-1)
                
        if self._plays.won() == True:
            print(WIN_TEXT)

        else:
            print(LOSE_TEST)

def main():
    GameApp()
    

if __name__ == "__main__":
    main()
