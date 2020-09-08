from kivy.atlas import Atlas
from kivy.core.image import Image as CoreImage
from chesswidget.SVGChessWidget import SVGChessWidget
from os import path

import chess
import sys


class AtlasChessWidget(SVGChessWidget):
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

    def piece_texture(self, piece: chess.Piece):
        return self.atlas[piece.symbol()]
