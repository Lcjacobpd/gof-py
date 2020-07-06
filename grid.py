# grid.py
# defines the space in which the individual cells exist

# Cell Rules:
#    1. Cells are either alive or dead
#    2. Cells have 8 neighbors (N,E,S,W and diagonals)
#    3. Neighbors outside the bounds of the grid are assumed dead

# Rules of the Grid:
#    1. Any live cell with fewer than two live white neighbors dies
#    2. Any live cell with 2-3 live neighbors lives on to the next generation
#    3. Any live cell with more than 3 live neighbors dies
#    4. Any dead cell with 3 live neighbors becomes alive

import random
import csv
import time
from os import system

COLOR_RED    = "\u001b[31m"
COLOR_CYAN   = "\u001b[36m"
COLOR_YELLOW = "\u001b[33m"
COLOR_GRAY   = "\u001b[1;30m"
COLOR_WHITE  = "\u001b[0m"


class Grid:
     
    '''
    Constructs an instance of a gridspace (width, height)
    '''
    def __init__(self, width, height):
        self.height = height
        self.width  = width
        self.matrix = []

        #each cell has x, y, status (0 = dead, 1 = alive)
        for x in range(width):
            column = []
            for y in range(height):
                column.append({'x': x, 'y': y, 'status': 0})
            self.matrix.append(column)


    '''
    Randomly populates the cells of a grid
    '''
    def populate(self):
        for x in range(self.width):
            for y in range(self.height):
                self.matrix[x][y]['status'] = random.choice([1,0])
    

    '''
    Create datagrid from template file (file name)
    '''
    def template(filename):
        with open(filename, 'rt') as f:
            rows = csv.reader(f)
            header = next(rows) #header contains grid dimmensions
            
            print()
            print(f"Reading {filename} with dimensions:", header)
            w = int(header[0])
            h = int(header[1])    
        
            #create new grid to populate
            preset = Grid(w, h)
            xpos = 0
            ypos = 0
            
            #convert document lines to grid rows
            for row in rows: 
                xpos = 0
                for char in row[0]:
                    preset.matrix[ypos][xpos]['status'] = int(char)
                    xpos += 1
                ypos += 1 
            return  preset
        
        
    '''
    Writes the current grid data to a text file (file name)
    '''
    def save(self, filename):
        with open(filename, 'wt') as f:
            f.write(f"{self.width},{self.height}\n") #grid dimensions in header
            
            for x in range(self.width):
                for y in range(self.height):
                    f.write(str(self.matrix[x][y]['status']))
                f.write('\n')
                
                
    '''
    Creates a label for the grid display in the terminal
    '''
    def label(self, generation, generations=0):
        if generations == 1: 
            print("\n")
            return #no lable for 'next'
            
        print("Generation: \t", generation)
        print("---" * self.width, end="-\n")
            
    
    '''
    Displays the current grid configuration
    '''
    def display(self):
        #column numbers
        print(COLOR_RED, end="")
        for x in range(self.height):
            print(f"{x:2d}", end=" ")
        print(COLOR_WHITE)

        for x in range(self.width):
            #row numbers
            print(COLOR_CYAN + F"{x:2d}", end=COLOR_WHITE)
            
            for y in range(self.height):
                if self.matrix[x][y]['status'] == 1:
                    print(COLOR_YELLOW + " ■ ", end=COLOR_WHITE) #living
                else:
                    print(COLOR_CYAN + " □ ", end=COLOR_WHITE) #dead
            print()
            
    '''
    Counts the number of currently living cells in the grid (None)
    '''
    def census(self):
        count = 0
        for x in range(self.width):
            for y in range(self.height):
                count += self.matrix[x][y]['status'] #alive = 1
        return count
        
    
    '''
    Counts the number of living neighbors (x, y positions)
    '''
    def check_neighbors(self, x, y):
        neighbor_count = 0
        
        if x > 0:
            neighbor_count += self.matrix[x-1][y]['status'] #alive = 1
            if y > 0: neighbor_count += self.matrix[x-1][y-1]['status']
            if y < h: neighbor_count += self.matrix[x-1][y+1]['status']
        
        if x < w:
            neighbor_count += self.matrix[x+1][y]['status']
            if y > 0: neighbor_count += self.matrix[x+1][y-1]['status']
            if y < h: neighbor_count += self.matrix[x+1][y+1]['status']

        if y > 0: neighbor_count += self.matrix[x][y-1]['status']
        if y < h: neighbor_count += self.matrix[x][y+1]['status']
        
        return neighbor_count
        
        
    '''
    Prints the statistics of the current grid configuration (Living, Born, Deaths, Survivors)
    '''
    def stats(self, living, births, deaths, survivors):
        print(f"Before: {living:>3}")
        print(f"       +{births:>3d} (born)")
        print(f"       -{deaths:>3d} (died)")
        print(f"After:  {self.census():3d} ({survivors} survivors)")
        print()
    
    
    '''
    Display several generations of the grid
    '''
    def iterate(self, generations, display_all=True, frame_delay=0):
        #lifetime statistics variables
        total_died = 0;
        total_born = 0;
        
        #display initial grid with label
        if display_all:
            self.label(0, generations)
            self.display()
            print()
        
        #process grid generations
        for i in range(generations):
            time.sleep(frame_delay) #apply delay
            
            #create next generation according to the grid rules
            subsequent_matrix = []
            h = self.height - 1
            w = self.width  - 1

            #generation statistics
            living = self.census()
            births    = 0
            deaths    = 0
            survivors = 0
            stale = True
            
            for x in range(self.width):
                sub_column = []
                for y in range(self.height):
                    cell = self.matrix[x][y]

                    neighbor_count = self.check_neighbors(x,y)

                    #check grid rules    
                    if cell['status'] == 1: #living cell
                        if neighbor_count < 2: #rule 1
                            sub_column.append({'x':x, 'y':y, 'status':0})
                            deaths += 1
                            total_died += 1
                            stale = False

                        elif neighbor_count < 4: #rule 2
                            sub_column.append({'x':x, 'y':y, 'status':1})
                            survivors += 1

                        elif neighbor_count > 3: #rule 3
                            sub_column.append({'x':x, 'y':y, 'status':0})
                            deaths += 1
                            total_died += 1
                            stale = False

                    else: #dead cell
                        if neighbor_count == 3: #rule 4
                            sub_column.append({'x':x, 'y':y, 'status':1})
                            births += 1
                            total_born += 1
                            stale = False

                        else: #default = dead
                            sub_column.append({'x':x, 'y':y, 'status':0})
    
                subsequent_matrix.append(sub_column)
            self.matrix = subsequent_matrix #update matrix

            #label generation & display generation statistics
            if display_all:
                clear_frame()
                self.label(i+1)
                self.display()
                self.stats(living, births, deaths, survivors)
            
            #if stale stop iterations (not for 'next' command)
            if stale:
                clear_frame()
                self.label(i+1, generations)
                self.display()
                print()
                print("Grid is stagnant; stopping life cycle...")
                return
                
        
        #display last generation if none of the rest
        if display_all == False: 
            clear_frame()
            print("\n")
            self.display()
            self.stats(living, births, deaths, survivors)
        
        #display lifetime statistics
        time.sleep(frame_delay)
        print("Lifetime statistics:")
        print(f"born:     {total_born:>3d}")
        print(f"died:     {total_died:>3d}")
        print()


    '''
    Skip forward a set number of generations (num)
    '''
    def jump_to(self, n, display=False):
        clear_frame()
        if n > 1:
            print(f"Skipping forward {n} generations...")
        self.iterate(n, display) #iterate showing only last generation
    
    '''
    Shows the next generation of the grid (None)
    '''
    def next(self):
        self.iterate(1, False) #step size, don't display all



