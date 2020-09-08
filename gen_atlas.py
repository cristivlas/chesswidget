import chess
import chess.svg
import cairosvg
import io
import json
from PIL import Image


def gen_piece_img(piece_type: chess.PieceType, color: chess.Color, size):
    piece = chess.Piece(piece_type, color)
    svg = chess.svg.piece(piece)
    png = cairosvg.svg2png(bytestring=svg, output_width=size, output_height=size, dpi=72)
    return Image.open(io.BytesIO(png))


def gen_piece_atlas(name='pieces', dpi=72, size=72):
    all = Image.new('RGBA', size=(size*6,size*2))
    atlas = {}
    for color in [chess.BLACK, chess.WHITE]:
        for piece_type in chess.PIECE_TYPES:
            im = gen_piece_img(piece_type, color, size)
            x, y = piece_type*size-size, color*size
            all.paste(im, [x,y], im)
            atlas[chess.Piece(piece_type, color).symbol()] = [x,all.size[1]-y-size,size,size]
    fname = name + '.png'
    all.save(fname, dpi=[dpi, dpi])
    with open(name + '.atlas', 'w') as f:
        json.dump({fname: atlas}, f)


def gen_board_img(fname='board.png', dpi=72, square_size=72):
    svg = chess.svg.board(board=None, size=8*square_size, flipped=True)
    png = cairosvg.svg2png(bytestring=svg)
    Image.open(io.BytesIO(png)).save(fname, dpi=[dpi, dpi])


if __name__ == '__main__':
    gen_piece_atlas()
    gen_board_img()