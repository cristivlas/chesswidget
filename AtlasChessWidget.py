from kivy.atlas import Atlas
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Line, Rectangle
from kivy.utils import get_color_from_hex
from chesswidget.ChessWidget import ChessWidget
from os import path

import chess
import chess.svg
import sys

SVG_MARGIN = 15


class AtlasChessWidget(ChessWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.board_tex = None
        self.margin = SVG_MARGIN

    def set_textures(self, atlas, board):
        self.atlas = atlas + '.atlas'
        self.board = board
        dir = path.dirname(sys.argv[0])
        if not path.isabs(self.atlas):
            self.atlas = path.join(dir, self.atlas)
        if not path.isabs(self.board):
            self.board = path.join(dir, self.board)
        self.atlas = Atlas(self.atlas)

    def board_texture(self):
        if self.board_tex is None:
            self.board_tex = CoreImage(self.board + '-{}.png'.format(self.flip)).texture
        return self.board_tex

    def rotate(self):
        self.board_tex = None
        super().rotate()

    def highlight_area(self, group, i, x, y, w, h):
        color = ['#aaa23b', '#cdd16a']
        group.add(Color(*get_color_from_hex(color[i])))
        if group == self.selection:
            group.add(Line(points=[x, y, x+w, y, x+w, y+h, x, y+h, x, y], width=3))
        else:
            assert group == self.highlight
            group.add(Rectangle(pos=(x, y), size=(w, h)))

    def piece_texture(self, piece: chess.Piece):
        return self.atlas[piece.symbol()]

    def recalc(self, size):
        self.board_size = min(size)
        self.scale = self.board_size / (2 * SVG_MARGIN + 8 * chess.svg.SQUARE_SIZE)
        self.margin = SVG_MARGIN * self.scale
        self.square_size = chess.svg.SQUARE_SIZE * self.scale
        self.board_pos = [(i - self.board_size) / 2 for i in size]
        self.xyo = [i + self.margin for i in self.board_pos]
