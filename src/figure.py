from os import environ
if 'PYGAME_HIDE_SUPPORT_PROMPT' not in environ:
    environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hidden'
del environ
import pygame
from pygame import Surface
from random import randint
from typing import Tuple,List
from image import pygame_img_resize


FIGURES = [
    [1,3,5,7],
    [2,4,5,7],
    [3,5,4,6],
    [3,5,4,7],
    [2,3,5,7],
    [3,5,7,6],
    [2,3,4,5]]

class Point:
    def __init__(self, x:int=0, y:int=0):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f'Point({self.x, self.y})'

    def copy(self):
        return Point(self.x, self.y)

    def __eq__(self, outer) -> bool:
        return self.x == outer.x and self.y == outer.y

class Piece:
    def __init__(self, pos:Tuple[int,int]=(0,0)):
        self.index_figure = -1
        self.points = [Point(0,0) for _ in range(4)]
        self.img = None
        self.empty_block_img = None
        self.pos = pos

    def set_piece(self, index_figure:int, blocks:List[Surface]):
        global FIGURES
        self.index_figure = index_figure
        empty_block, *piece_blocks = blocks
        self.empty_block_img = empty_block
        self.img = piece_blocks[index_figure]
        maxy = float('-infinity')
        for index, point in enumerate(self.points):
            point.x = FIGURES[index_figure][index] % 2
            point.y = FIGURES[index_figure][index] // 2
            maxy = max([maxy, point.y])
        self.move_to(0, 0)

    def set_random_piece(self, blocks:List[Surface]):
        self.set_piece(randint(0,6), blocks)

    def set_pos(self, x:int, y:int):
        self.pos = (x,y)

    def rotate(self):
        aux = self.points[1]
        for point in self.points:
            x = point.y-aux.y
            y = point.x-aux.x
            point.x = aux.x-x
            point.y = aux.y+y
        
    def get_box(self) -> Tuple[int,int,int,int]:
        
        min_x = float('infinity')
        min_y = float('infinity')
        max_x = -min_x
        max_y = -min_y

        for point in self.points:
            if point.x < min_x:
                min_x = point.x
            elif point.x > max_x:
                max_x = point.x
            if point.y < min_y:
                min_y = point.y
            elif point.y > max_y:
                max_y = point.y
        return (min_x, max_x, min_y, max_y)

    def move_to(self, x:int, y:int):
        (min_x, _, min_y, _) = self.get_box()
        for point in self.points:
            point.x += x - min_x
            point.y += y - min_y
    
    def move_or_rotate(self, dir:str):
        x = 0
        if dir in ['left','a']:
            x = -1
        elif dir in ['right','s']:
            x = 1
        else:
            return None

        for point in self.points:
            point.x += x

    def update(self):
        for point in self.points:
            point.y += 1

    def check(self, maxx, maxy):
        for point in self.points:
            if not (-1 < point.x < maxx and -1 < point.y < maxy):
                return False
        return True

    def draw(self, display:Surface, no_clear:bool=True):
        x, y = self.pos
        block_w, block_h = self.img.get_size()
        img = self.img if no_clear else self.empty_block_img
        for point in self.points:
            display.blit(img,(x+point.x*block_w, y+point.y*block_h))

    def copy(self):
        new = Piece()
        new.img = self.img
        new.pos = self.pos
        new.index_figure = self.index_figure
        new.empty_block_img = self.empty_block_img
        new.points = [point.copy() for point in self.points]
        return new

def create_list_blocks_img(filename:str, size=None) -> List[Surface]:
    image = pygame.image.load(filename)
    n_blocks = image.get_width()//32
    blocks = [Surface((32,32)) for _ in range(n_blocks)]
    for index, block in enumerate(blocks):
        block.blit(image, (0,0), (index*32,0,32,32))
        if size:
            blocks[index] = pygame_img_resize(block, size)
    return blocks


class Board:

    def __init__(self, height:int, width:int):
        self.width = width
        self.height = height
        self.blocks = [[-1 for _ in range(width)] for _ in range(height)]
        self.box_region = [0, width, 0, height]

    def __getitem__(self, key:Tuple[int,int]):
        if isinstance(key, tuple) and len(key)==2:
           row, column = key
           return self.blocks[row][column]
        raise TypeError('invalide key value')

    def reset(self):
        for row in range(self.height):
            for column in range(self.width):
                self.blocks[row][column] = -1

    def __setitem__(self, key:Tuple[int,int], value:int):
        if isinstance(key, tuple) and len(key)==2:
           row, column = key
           self.blocks[row][column] = value
        else:
            raise TypeError('invalide key value')

    def draw_background(self, display:Surface, pos: Tuple[int,int], blocks:List[Surface]):
        x, y = pos
        empty_block = blocks[0]
        block_w,block_h = empty_block.get_size()

        for row in range(self.height):
            for column in range(self.width):
                display.blit(empty_block,(x+column*block_w, y+row*block_h))
        pygame.draw.rect(display, (80,80,80),[x-2,y-2,self.width*block_w+4,self.height*block_h+4],2)

    def draw(self, display:Surface, pos: Tuple[int,int], blocks:List[Surface]):
        x, y = pos
        block_w,block_h = blocks[0].get_size()
        [_, *piece_blocks] = blocks

        for row in range(self.height):
            for column in range(self.width):
                value = self.blocks[row][column]
                if value > -1:
                    display.blit(piece_blocks[value],(x+column*block_w, y+row*block_h))
        

    def check(self, piece:Piece) -> bool:
        for point in piece.points:
            x,y = (point.x, point.y)
            if not ((-1 < x < self.width) and (-1 < y < self.height)):
                return False
            if self.blocks[y][x] != -1:
                return False
        return True

    def board_score(self, display:Surface, empty_block:Surface, pos:Tuple[int,int]) -> int:
        score = 0
        x,y = pos
        row_aux = self.height - 1
        block_w,block_h = empty_block.get_size()

        for row in range(self.height-1, 0,-1):
            n_blocks = 0
            for column in range(self.width):
                n_blocks += self.blocks[row][column] != -1
                self.blocks[row_aux][column] = self.blocks[row][column]
                display.blit(empty_block,(x+column*block_w, y+(row)*block_h))
            if n_blocks == self.width:
                score += 1
            else:
                row_aux -= 1
        return score

    def add_piece(self, piece:Piece):

        for point in piece.points:
            x,y = point.x,point.y
            try:
                self.blocks[y-1][x] = piece.index_figure
            except:
                raise IndexError