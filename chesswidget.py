from kivy.uix.widget import Widget
from kivy.graphics import *
from kivy.core.image import Image as CoreImage

import cairosvg
import chess
import chess.svg
import io

SVG_MARGIN = 15


class ChessWidget(Widget):
    __events__ = ('on_user_move',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.margin = SVG_MARGIN
        self.board_pos = None
        self.bind(size = self.recalc)        
        self.bind(size = lambda *_: self.redraw())
        self.board = chess.Board()
        self.move = str()
        self.piece_tex = {}
        self.selection = InstructionGroup()
      
    def on_user_move(self, *_):
        pass

    def on_touch_down(self, touch):
        x,y = [(i - j) / self.square_size for i, j in zip(touch.pos, self.xyo)]
        if 0 <= x < 8 and 0 <= y < 8:
            move = 'abcdefgh'[int(x)] + str(1 + int(y))
            self.move += move
            if len(self.move) < 4:
                self.select(move)
            else:
                self.dispatch('on_user_move', self.move)
                self.move = str()

    def update(self, fen, history, move):
        self.board.set_fen(fen)
        self.redraw(move)

    def piece_texture(self, piece: chess.Piece):
        tex = self.piece_tex.get(piece.symbol, None)
        if tex is None:
            size = self.square_size
            svg = chess.svg.piece(piece)
            png = cairosvg.svg2png(bytestring=svg, dpi=36, output_width=size, output_height=size)
            self.piece_tex[piece.symbol] = tex = CoreImage(io.BytesIO(png), ext='png').texture
        return tex

    # recalculate position, size, scale, etc.
    def recalc(self, _, size):
        self.board_size = min(size)
        self.scale = self.board_size / (2 * SVG_MARGIN + 8 * chess.svg.SQUARE_SIZE)
        self.margin = SVG_MARGIN * self.scale
        self.square_size = chess.svg.SQUARE_SIZE * self.scale
        self.board_pos = [(i - self.board_size) / 2 for i in size]
        self.xyo = [i + self.margin for i in self.board_pos]

    def redraw(self, move=None):
        if self.board_pos: # recalc ran?
            svg = chess.svg.board(board=None, size=self.board_size, lastmove=move)
            png = cairosvg.svg2png(bytestring=svg)
            img = CoreImage(io.BytesIO(png), ext='png')
            self.canvas.clear()
            with self.canvas:
                Color(1,1,1,1)
                Rectangle(pos=self.board_pos, size=2*[self.board_size])
                Rectangle(pos=self.board_pos, size=2*[self.board_size], texture=img.texture)
                self.redraw_pieces()

    def redraw_pieces(self):
        size = 2 * [self.square_size]
        for square, piece in self.board.piece_map().items():
            x, y = self.xy(square % 8, square // 8)
            Rectangle(pos=(x, y), size=size, texture=self.piece_texture(piece))
    
    def select(self, move):
        self.selection.clear()
        w, h = 2*[self.square_size]        
        for pos in [move[i:i+2] for i in range(0, len(move), 2)]:
            x, y = [j for j in self.screen_coords(*pos)]
            self.selection.add(Color(0.5, 0.65, 0.5, 1))
            self.selection.add(Line(points=[x, y, x+w, y, x+w, y+h, x, y+h, x, y], width=2))
        if self.canvas.indexof(self.selection) < 0:
            self.canvas.add(self.selection)

    def screen_coords(self, file, rank):
        col, row = 'abcdefgh'.index(file), int(rank) - 1
        return [o + i * self.square_size for o, i in zip(self.xyo, [col, row])]

    def xy(self, col, row):
        return [o + i * self.square_size for o, i in zip(self.xyo, [col, row])]
