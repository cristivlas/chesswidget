from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Line, Rectangle
from kivy.utils import get_color_from_hex

from chesswidget.ChessWidget import ChessWidget
from chess import Piece
import chess.svg
import io

try:
    import cairosvg
except:
    pass

SVG_MARGIN = 15.0
SVG_SQUARE_SIZE = chess.svg.SQUARE_SIZE
ANCHOR = { 'bottom': 0, 'center': 0.5, 'left': 0, 'right': 1, 'top': 1 }


class SVGChessWidget(ChessWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anchor = [ 'center', 'center' ]
        self.piece_tex = {}
        self.board_tex = None
        self.margin = SVG_MARGIN

    def board_texture(self):
        if self.board_tex is None:
            svg = chess.svg.board(board=None, size=self.board_size, flipped=self.flip)
            png = cairosvg.svg2png(bytestring=svg)
            self.board_tex = CoreImage(io.BytesIO(png), ext='png', dpi=72).texture
        return self.board_tex

    def highlight_area(self, group, i, x, y, w, h):
        color = ['#aaa23b', '#cdd16a']
        group.add(Color(*get_color_from_hex(color[i])))
        if group == self.selection:
            group.add(Line(points=[x, y, x+w, y, x+w, y+h, x, y+h, x, y], width=3))
        else:
            assert group == self.highlight
            lw = self.grid_line_width
            group.add(Rectangle(pos=(x+lw, y+lw), size=(w-2*lw, h-2*lw)))

    def gen_texture(self, piece):
        size = self.square_size
        svg = chess.svg.piece(piece)
        png = cairosvg.svg2png(bytestring=svg, output_width=size, output_height=size, dpi=72)
        return CoreImage(io.BytesIO(png), ext='png').texture

    def piece_texture(self, piece: chess.Piece):
        sym = piece.symbol()
        tex = self.piece_tex.get(sym, None)
        if tex is None:
            tex = self.piece_tex[sym] = self.gen_texture(piece)
        return tex

    def recalc(self, size):
        self.board_size = min(size)
        self.scale = self.board_size / (2 * SVG_MARGIN + 8 * SVG_SQUARE_SIZE)
        self.margin = SVG_MARGIN * self.scale
        self.square_size = SVG_SQUARE_SIZE * self.scale
        self.board_pos = [(i - self.board_size) * ANCHOR[j] for i, j in zip(self.parent.size, self.anchor)]
        self.xyo = [i + self.margin for i in self.board_pos]

    def rotate(self):
        self.board_tex = None
        super().rotate()
