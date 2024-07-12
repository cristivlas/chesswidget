from kivy.atlas import Atlas
from kivy.core.image import Image as CoreImage
from chesswidget.SVGChessWidget import SVGChessWidget
from os import getcwd, path

import chess
import sys


class AtlasChessWidget(SVGChessWidget):
    def set_textures(self, atlas, board):
        self.atlas = atlas + '.atlas'
        self.board = board
        #dir = path.dirname(sys.argv[0])
        dir = getcwd()
        if not path.isabs(self.atlas):
            self.atlas = path.join(dir, self.atlas)
        if self.board and not path.isabs(self.board):
            self.board = path.join(dir, self.board)
        self.atlas = Atlas(self.atlas)

    def board_texture(self):
        pass

    def rotate(self):
        self.board_tex = None
        super().rotate()

    def piece_texture(self, piece: chess.Piece):
        return self.atlas[piece.symbol()]
