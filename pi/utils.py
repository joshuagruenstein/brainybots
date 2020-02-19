import math
import numpy as np

class Maze:
    LINES = [ # in 10ths of inches
        [20, 140,260,140],
        [140,140,140,260],
        [260,260,380,260],
        [260,260,260,380],
        [20, 20, 380, 20],
        [20, 20, 20, 380],
        [20, 380,380,380],
        [380, 20,380,380],
    ]
    
    INCH_TO_CM = 2.54
    CM_TO_INCH = 1/INCH_TO_CM
    DEG_TO_RAD = 0.0174533
    ROBOT_RADIUS = 30 # in 10ths of inches, really radius to sensor
    
    @staticmethod
    def line_intersection(l1, l2):
        #returns None if no intersection, otherwise point of intersection

        s1_x, s1_y = l1[2] - l1[0], l1[3] - l1[1]
        s2_x, s2_y = l2[2] - l2[0], l2[3] - l2[1]
  
        try:
            s = (-s1_y * (l1[0] - l2[0]) + s1_x * (l1[1] - l2[1])) / (-s2_x * s1_y + s1_x * s2_y)
            t = ( s2_x * (l1[1] - l2[1]) - s2_y * (l1[0] - l2[0])) / (-s2_x * s1_y + s1_x * s2_y)
        except ZeroDivisionError: # lines are parallel
            return
        
        if s >= 0 and s <= 1 and t >= 0 and t <= 1:
            return l1[0] + (t * s1_x), l1[1] + (t * s1_y)
    

    @staticmethod
    def simulatedDistance(x, y, angle):
        """Simulates distance sensor reading from a robot at
        a cell, pointed at a given angle.

        Parameters:
        x (float): the x position of the robot in the maze in cm
        y (float): the y position of the robot in the maze in cm
        angle (float): the angle in degrees, with 0 pointing up
        
        Returns:
        float: the simulated distance to a wall in centimeters.
        """
 
        x, y = 10*Maze.CM_TO_INCH*x + 20, 10*Maze.CM_TO_INCH*y + 20
        
        beam = [x, y,
            x + 500*math.cos(GridMaze.DEG_TO_RAD*angle),
            y + 500*math.sin(GridMaze.DEG_TO_RAD*angle)
        ]
        
        min_s = 10000000
        for line in GridMaze.LINES:
            intersection = GridMaze.line_intersection(beam, line)

            if intersection is None:
                continue

            min_s = min(min_s, math.sqrt(
                (beam[0] - intersection[0])**2 +
                (beam[1] - intersection[1])**2
            ))
        
        return (min_s - GridMaze.ROBOT_RADIUS)*GridMaze.INCH_TO_CM/10   
    

class GridMaze(Maze):
    @staticmethod
    def cell_to_coords(cell):
        x, y = 60+120*(cell % 3), 60+120*(cell // 3)
        return GridMaze.INCH_TO_CM*x/10, GridMaze.INCH_TO_CM*y/10

    @staticmethod
    def simulatedDistance(cell, angle):
        """Simulates distance sensor reading from a robot at
        a cell, pointed at a given angle.

        Parameters:
        cell (int): the cell in the maze (0 through 8 inclusive)
        angle (float): the angle in degrees, with 0 pointing up
        
        Returns:
        float: the simulated distance to a wall in centimeters.
        """
        
        x, y = GridMaze.cell_to_coords(cell)
        return super(GridMaze,GridMaze).simulatedDistance(x, y, angle)

def gaussian(x, mu, sigma):
    """Evaluates the pdf of a normal distribution with mean
    mu and standard deviation sigma at point x.

    Parameters:
    x (float): the value to evaluate the PDF at
    mu (float): the mean of the normal distribution
    sigma (float): the standard deviation of the normal distribution

    Returns:
    float: the result of the PDF at point x (between 0 and 1).
    """
    
    return np.exp(-0.5*((x-mu)/sigma)**2)/(sigma*np.sqrt(2*np.pi))