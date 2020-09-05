from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Line, Rectangle
from kivy.utils import get_color_from_hex

from chesswidget.ChessWidget import ChessWidget
import cairosvg
import chess
import chess.svg
import io

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
            self.board_tex = CoreImage(io.BytesIO(png), ext='png', dpi=72).texture
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
            png = cairosvg.svg2png(bytestring=svg, output_width=size, output_height=size, dpi=72)
            tex = CoreImage(io.BytesIO(png), ext='png').texture
            self.piece_tex[piece.symbol] = tex
        return tex

    def recalc(self, size):
        self.board_size = min(size)
        self.scale = self.board_size / (2 * SVG_MARGIN + 8 * chess.svg.SQUARE_SIZE)
        self.margin = SVG_MARGIN * self.scale
        self.square_size = chess.svg.SQUARE_SIZE * self.scale
        self.board_pos = [(i - self.board_size) / 2 for i in size]
        self.xyo = [i + self.margin for i in self.board_pos]
