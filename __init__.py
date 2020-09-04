from kivy.core.image import Image as CoreImage
from kivy.graphics import *
from kivy.utils import get_color_from_hex
from kivy.uix.widget import Widget

import cairosvg
import chess
import chess.svg
import io
import math

class ChessWidget(Widget):
    __events__ = ('on_user_move',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size = self.on_size)
        self.bind(size = lambda *_: self.redraw())
        self.board = chess.Board()
        self.board_pos = None
        self.square_size = None
        self.xyo = [0, 0]   # xy origin for squares (not the origin of the board, which may include coords)
        self.move = str()   # pending move, uci notation
        self.selection = InstructionGroup()
        self.highlight = InstructionGroup()
        self.clear_color = (1,1,1,1)

    def on_touch_down(self, touch):
        x,y = [(i - j) / self.square_size for i, j in zip(touch.pos, self.xyo)]
        if 0 <= x < 8 and 0 <= y < 8:
            move = 'abcdefgh'[int(x)] + str(1 + int(y))
            self.move += move
            if len(self.move) < 4:
                self.highlight_move(move)
            elif self.dispatch('on_user_move', self.move):
                self.move = str()
            else:
                self.highlight_move(move)
                self.move = move

    def on_user_move(self, *_):
        pass

    def on_size(self, _, size):
        self.recalc(size)
        self.redraw_board()

    def update(self, fen, history, move):
        self.board.set_fen(fen)
        self.redraw(move)

    def board_texture(self):
        pass

    def highlight_area(self, group, i, x, y, w, h):
        pass

    def piece_texture(self, piece: chess.Piece):
        pass

    def recalc(self, size):
        pass

    def redraw(self, move=None):
        if self.board_pos:
            self.redraw_pieces(move)

    def redraw_board(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.clear_color)
            Rectangle(pos=self.board_pos, size=2*[self.board_size])
            Rectangle(pos=self.board_pos, size=2*[self.board_size], texture=self.board_texture())

    def redraw_pieces(self, move):
        self.canvas.clear()
        with self.canvas:
            if move:
                self.highlight_move(move.uci())
            size = 2 * [self.square_size]
            for square, piece in self.board.piece_map().items():
                x, y = self.screen_coords(square % 8, square // 8)
                Rectangle(pos=(x, y), size=size, texture=self.piece_texture(piece))

    def highlight_move(self, move):
        group = self.highlight if len(move) >= 4 else self.selection
        group.clear()
        w, h = 2*[self.square_size]
        for i, pos in enumerate([move[i:i+2] for i in range(0, min(4, len(move)), 2)]):
            x, y = [j for j in self.screen_coords(*pos)]
            self.highlight_area(group, i, x, y, w+1, h+1)
        if self.canvas.indexof(group) < 0:
            self.canvas.add(group)
        group.add(Color(*self.clear_color))

    def screen_coords(self, col, row):
        if isinstance(col, str):
            assert col in 'abcdefgh'    # expect file-rank
            assert int(row) in range(1, 9)
            col, row = 'abcdefgh'.index(col), int(row) - 1
        return [math.ceil(o + i * self.square_size)-1 for o, i in zip(self.xyo, [col, row])]


SVG_MARGIN = 15

class SVGChessWidget(ChessWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.piece_tex = {}
        self.board_tex = None
        self.margin = SVG_MARGIN

    def board_texture(self):
        if self.board_tex is None:
            svg = chess.svg.board(board=None, size=self.board_size)
            png = cairosvg.svg2png(bytestring=svg)
            self.board_tex = CoreImage(io.BytesIO(png), ext='png').texture
        return self.board_tex

    def highlight_area(self, group, i, x, y, w, h):
        color = ['#aaa23b', '#cdd16a']
        group.add(Color(*get_color_from_hex(color[i])))
        if group == self.selection:
            group.add(Line(points=[x, y, x+w, y, x+w, y+h, x, y+h, x, y], width=3))
        else:
            assert group == self.highlight
            group.add(Rectangle(pos=(x, y), size=(w, h)))

    def piece_texture(self, piece: chess.Piece):
        tex = self.piece_tex.get(piece.symbol, None)
        if tex is None:
            size = self.square_size
            svg = chess.svg.piece(piece)
            png = cairosvg.svg2png(bytestring=svg, output_width=size, output_height=size)
            self.piece_tex[piece.symbol] = tex = CoreImage(io.BytesIO(png), ext='png').texture
        return tex

    def recalc(self, size):
        self.board_size = min(size)
        self.scale = self.board_size / (2 * SVG_MARGIN + 8 * chess.svg.SQUARE_SIZE)
        self.margin = SVG_MARGIN * self.scale
        self.square_size = chess.svg.SQUARE_SIZE * self.scale
        self.board_pos = [(i - self.board_size) / 2 for i in size]
        self.xyo = [i + self.margin for i in self.board_pos]
