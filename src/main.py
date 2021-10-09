from os import environ
if 'PYGAME_HIDE_SUPPORT_PROMPT' not in environ:
    environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hidden'
del environ
import json
import pygame
from os.path import normpath
from image import pill_img_open_and_resize
from figure import create_list_blocks_img,Board,Piece


class Game:

    def __init__(self):
        self.config()

    def config(self):
        pygame.init()
        pygame.mixer.init()
        pygame.font.init()

        self.SCREEN_W = 460
        self.SCREEN_H = 500
        pygame.display.set_caption('TetrisGame v1.1.2')
        pygame.display.set_icon(pygame.image.load('./images/icon.png'))
        self.display = pygame.display.set_mode((self.SCREEN_W,self.SCREEN_H))
        
        self.is_pause = False
        self.background = None
        self.piece = Piece()
        self.next_piece = Piece()
        self.temp_piece = Piece()
        self.board = Board(23,12)
        self.score = 0
        self.max_score = self.load_file_score()
        self.START_POSITION_PIECE_X = 5
        self.pause_img = pill_img_open_and_resize('./images/pause.png', (50,50))
        self.block_pieces = create_list_blocks_img('./images/peca.png', size=(20,20))
        self.clock = pygame.time.Clock()

        font = pygame.font.SysFont('Verdana', 10)      
        self.text_pause = font.render(f'Pause', True, (255,255,255))
        font = pygame.font.SysFont('Verdana', 20)
        font.set_bold(True)
        self.font = font

        self.open_sound_config()

    def draw_or_hidden_pause(self, x:int, y:int):
        width, height = self.pause_img.get_size()
        text_height = self.text_pause.get_height()
        pygame.draw.rect(self.display, (0), (x, y, width, height+text_height))
        self.is_pause = not self.is_pause

        if self.is_pause:
            text_width = (self.text_pause.get_width()-width)//2
            self.display.blit(self.pause_img,(x, y))
            self.display.blit(self.text_pause, (x-text_width, y+height))

    def update_and_draw_scores(self):
        font = self.font
        pygame.draw.rect(self.display, 0, (290,160,150,120))
        text_score = font.render(f'score:', True, (255,255,255))
        self.display.blit(text_score,(290,160))
        text_score = font.render(f'{self.score:09d}', True, (255,255,255))
        self.display.blit(text_score,(300,190))

        text_max_score = font.render(f'max score:', True, (255,255,255))
        self.display.blit(text_max_score,(290, 220))
        text_max_score = font.render(f'{self.max_score:09d}', True, (255,255,255))
        self.display.blit(text_max_score,(300,250))

    def draw_next_piece(self):
        font = self.font
        pygame.draw.rect(self.display, 0, (290,20,150,140))
        text = font.render(f'next piece:', True, (255,255,255))
        self.display.blit(text,(300,20))
        self.next_piece.set_pos(340,60)
        self.next_piece.draw(self.display)

    def move_or_rotate_piece(self, current_key) -> bool:
        if current_key in ['up','w'] and self.piece.index_figure != 6:
            self.piece.rotate()
        else:
            self.piece.move_or_rotate(current_key)

        if not self.board.check(self.piece):
            self.piece = self.temp_piece.copy()
            self.piece.update()
            if not self.board.check(self.piece):
                self.piece.move_to(self.START_POSITION_PIECE_X, 0)
            return True
        return False

    def run_loop(self):

        FPS = 2
        FPS_ACCUMULATOR = FPS
        FPS_INCREMENT = 0.125
        SIZE = 20
        XMAX, YMAX = (23, 20)
        OFFSETX = SIZE
        KEY_PRESS_DELAY = 40
        SCORE_TO_NEXT_VELOCITY = 80
        SCORE_INCREMENT = 100

        ticks = 0
        game = True
        key_pressed = False
        current_key = None
        self.score = 0
        list_scores = [0, 10, 30, 60, 100]
        valid_keys = ['left','right','down','up','w','a','s','z']

        self.background = pygame.Surface((XMAX*SIZE,YMAX*SIZE))
        
        blocks = self.block_pieces
        board = self.board
        board.draw_background(self.display, (OFFSETX, 20), blocks)
        self.piece = Piece((OFFSETX, 20))
        self.piece.set_random_piece(blocks)
        self.next_piece.set_random_piece(blocks)
        self.piece.move_to(self.START_POSITION_PIECE_X,0)
        self.temp_piece = self.piece.copy()
        
        self.update_and_draw_scores()
        

        while game:
            
            self.clock.tick(FPS)
            FPS = FPS_ACCUMULATOR

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    game = False
                    break
                elif e.type == pygame.KEYDOWN:
                    key = pygame.key.name(e.key)
                    if key in ['escape']:
                        game = False
                        break
                    elif key in valid_keys:
                        ticks = pygame.time.get_ticks()
                        current_key = key
                        key_pressed = True
                        self.move_or_rotate_piece(key)
                    elif key in ['p', 'space']:
                        self.draw_or_hidden_pause(340,310)
                        pygame.display.flip()
                    
                elif e.type == pygame.KEYUP:
                    key_pressed = False
                    current_key = None

            if key_pressed:
                if current_key in ['z','down'] and FPS_ACCUMULATOR < 30:
                    FPS = 30
                elif (pygame.time.get_ticks()-ticks) > KEY_PRESS_DELAY:
                    FPS = FPS if self.move_or_rotate_piece(current_key) else 15

            if not self.is_pause and game:
                
                self.temp_piece.draw(self.display, False)
                self.piece.draw(self.display)
                self.draw_next_piece()
                self.temp_piece = self.piece.copy()
                self.piece.update()

                if not board.check(self.piece):

                    board.add_piece(self.piece)
                    self.piece.set_piece(self.next_piece.index_figure,blocks)
                    self.next_piece.set_random_piece(blocks)
                    self.piece.move_to(self.START_POSITION_PIECE_X, 0)
                    score = board.board_score(self.display, blocks[0], (OFFSETX,20))
                    
                    if score > 0:
                        score = list_scores[ score ]
                        self.play_score_sound()
                    self.score += score
                    self.update_and_draw_scores()

                    while self.score >= SCORE_TO_NEXT_VELOCITY:
                        SCORE_TO_NEXT_VELOCITY += SCORE_INCREMENT
                        FPS_ACCUMULATOR += FPS_INCREMENT
                    
                    if not board.check(self.piece):
                        pygame.mixer.music.stop()
                        game = self.show_screen_game_over()
                        if not game:
                            break
                        pygame.mixer.music.play(-1)
                        board.reset()
                        self.update_and_draw_scores()
                        board.draw_background(self.display, (OFFSETX,20), blocks)
                        FPS = 2
                        FPS_ACCUMULATOR = 2
                        self.max_score = self.save_score_in_file()
                        self.score = 0
                        self.update_and_draw_scores()
                        continue

                board.draw(self.display, (OFFSETX,20), blocks)
                pygame.display.flip()

        self.quit_game()

    def show_screen_game_over(self):
        list_piece = []
        for n_piece, index_figure in enumerate([2, 3, 4, 5]):
            piece = Piece((n_piece*100+60, 240))
            piece.set_piece(index_figure, self.block_pieces)
            list_piece.append(piece)

        self.play_game_over_sound()

        font = pygame.font.SysFont('Arial black', 50)
        font.set_bold(True)
        text = font.render('GAME OVER', True, (255,255,255))

        info = pygame.font.SysFont('default', 25)
        info.set_bold(True)
        text_info = info.render('press Enter to continue or ESC to quit.', True, (255,255,255))

        ticks = 0
        game = True
        next_game = False

        while game:
            ticks += self.clock.tick(30)
            
            self.display.fill((0))

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    game = False
                    break
                elif e.type == pygame.KEYDOWN:
                    key = pygame.key.name(e.key)
                    if key == 'escape':
                        game = False
                        break
                    elif key == 'return':
                        next_game = True
                        game = False
                        break
            if game:

                if 300 < ticks < 600:
                    self.display.blit(text, (40,100))
                if ticks > 600:
                    ticks = 0
                self.display.blit(text_info, (50,420))
                for piece in list_piece:
                    piece.draw(self.display)
                pygame.display.flip()

        return next_game

    def quit_game(self):
        pygame.quit()

    def load_file_score(self):
        try:
            file = open('score.txt')
        except FileNotFoundError:
            with open('score.txt','w') as file:
                for _ in range(5):
                    file.write('0\n')
            file = open('score.txt')
        with file:
            max_score = file.readline().strip()
        return int(max_score)

    def save_score_in_file(self) -> int:
        scores = []
        
        with open('score.txt') as file:
            for _ in range(5):
                scores += [ int(file.readline().strip()) ]

        with open('score.txt','w') as file:
            scores += [self.score]
            scores.sort(reverse=True)
            scores.pop()
            self.max_score = scores[0]
            for score in scores:
                file.writelines(f'{score}\n')

        return self.max_score

    def play_score_sound(self):
        if self.effect is not None:
            self.effect.play()

    def play_game_over_sound(self):
        if self.game_over is not None:
            self.game_over.play()

    def open_sound_config(self):
        self.effect = None
        self.game_over = None
        try:
            with open('sound.json','r') as file:
                data = json.load(file)
                path = data['music'].strip()
                if path!="":
                    pygame.mixer.music.load(normpath(path))
                    pygame.mixer.music.play(-1)
                path = data['score'].strip()
                if path!="":
                    self.effect = pygame.mixer.Sound(normpath(path))
                path = data['game-over'].strip()
                if path!="":
                    self.game_over = pygame.mixer.Sound(normpath(path))
        except:
            pygame.mixer.music.stop()
            self.effect = None
            self.game_over = None

game = Game()
game.run_loop()
