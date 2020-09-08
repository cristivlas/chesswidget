from kivy.graphics import Color, Rectangle, InstructionGroup
from kivy.uix.widget import Widget


class ChessWidget(Widget):
    __events__ = ('on_user_move',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size = self.on_size)
        self.bind(size = lambda *_: self.redraw())
        self.board_pos = None
        self.square_size = None
        self.xyo = [0, 0]   # xy origin for squares (not the board, which may include coords)
        self.move = str()   # pending move, uci notation
        self.selection = InstructionGroup()
        self.highlight = InstructionGroup()
        self.clear_color = (1,1,1,1)
        self.flip = 0

    def rotate(self):
        self.flip ^= 1
        self.recalc(self.size)
        self.redraw_board()
        self.redraw()

    def set_model(self, board):
        self.piece_map = board.piece_map

    def on_touch_down(self, touch):
        x,y = [(i - j) / self.square_size for i, j in zip(touch.pos, self.xyo)]
        if 0 <= x < 8 and 0 <= y < 8:
            if self.flip:
                x = 8 - x
                y = 8 - y
            move = 'abcdefgh'[int(x)] + str(1 + int(y))
            self.move += move
            if len(self.move) < 4:
                self.highlight_move(move)
            # click on a selected square? deselect it
            elif self.move[:2] == self.move[2:]:
                self.move = str()
                self.highlight_move(self.move)
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

    def update(self, move):
        self.redraw(move)

    def board_texture(self):
        pass

    def highlight_area(self, group, i, x, y, w, h):
        pass

    def piece_texture(self, piece):
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
            for square, piece in self.piece_map().items():
                col, row = square % 8, square // 8
                xy = self.screen_coords(col, row)
                Rectangle(pos=(xy), size=size, texture=self.piece_texture(piece))

    def highlight_move(self, move):
        group = self.highlight if len(move) >= 4 else self.selection
        group.clear()
        w, h = 2*[self.square_size]
        for i, pos in enumerate([move[i:i+2] for i in range(0, min(4, len(move)), 2)]):
            x, y = [j for j in self.screen_coords(*pos)]
            self.highlight_area(group, i, x, y, w+1, h+1)
        if self.canvas.indexof(group) < 0:
            self.canvas.add(group)
        if group.children:
            group.add(Color(*self.clear_color))

    def screen_coords(self, col, row):
        if isinstance(col, str):
            assert col in 'abcdefgh'    # expect file-rank
            assert int(row) in range(1, 9)
            col, row = 'abcdefgh'.index(col), int(row) - 1
        if self.flip:
            col = 7 - col
            row = 7 - row
        return [o + i * self.square_size for o, i in zip(self.xyo, [col, row])]

