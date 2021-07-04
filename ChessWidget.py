from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, InstructionGroup, Line, Rectangle
from kivy.uix.widget import Widget


class ChessWidget(Widget):
    __events__ = ('on_user_move',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size = self.on_size)
        self.board_pos = None
        self.margin = None
        self.square_size = None
        self.xyo = [0, 0]   # xy origin for squares (not the board, which may include coords)
        self.move = str()   # pending move, uci notation
        self.selection = InstructionGroup()
        self.highlight = InstructionGroup()
        self.clear_color = (1,1,1,1)
        self.flip = 0
        self.last_move = None
        self.grid_line_width = 1.25
        self.grid_color = (0,0,0,1)
        # coordinates of most recently highlighted square, in screen coordinates
        self.highlight_pos = (0,0)
        self.long_press_event = None

    def cancel_long_press(self, *_):
        if self.long_press_event:
            self.long_press_event.cancel()
            self.long_press_event = None

    def rotate(self):
        self.flip ^= 1
        self.recalc(self.size)
        self.redraw_board()
        self.redraw(self.last_move)

    def set_model(self, board):
        self.model = board
        self.last_move = None

    def inside(self, pos):
        board_size = self.board_size - 2 * self.margin
        return all([x >= x0 and x <= x0 + board_size for x, x0 in zip(pos, self.xyo)])

    def on_long_press(self, touch):
        pass

    def on_touch_down(self, touch):
        if self.inside(touch.pos):
            self.long_press_event = Clock.schedule_once(lambda *_: self.on_long_press(touch), 1)

    def on_touch_up(self, touch):
        self.cancel_long_press(touch)
        self._select_square(self._square_name_from_coords(touch.pos))

    def on_user_move(self, *_):
        self.move = str()

    def on_size(self, _, size):
        self.recalc(size)
        self.redraw_board()
        self.redraw(self.last_move)

    def _select_square(self, square):
        if square:
            self.move += square
            if len(self.move) < 4:
                self.highlight_move(square)
            # click on a selected square? deselect it
            elif self.move[:2] == self.move[2:]:
                self.move = str()
                self.highlight_move(self.move)
            elif self.dispatch('on_user_move', self.move):
                self.move = str()
            else:
                self.highlight_move(square)
                self.move = square

    def update(self, move):
        self.redraw(move)
        self.last_move = move

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
        if self.board_pos and self.board_size:
            self.canvas.before.clear()
            with self.canvas.before:
                Rectangle(pos=self.board_pos, size=2*[self.board_size], texture=self.board_texture())
                self.redraw_grid()

    def redraw_grid(self):
        Color(*self.grid_color)
        y = self.board_pos[1]+self.margin
        for i in range(9):
            x = self.board_pos[0] + self.margin + self.square_size * i
            Line(points=[x, y, x, y + 8*self.square_size], width=self.grid_line_width)
        x = self.board_pos[0]+self.margin
        for i in range(9):
            y = self.board_pos[1] + self.margin + self.square_size * i
            Line(points=[x, y, x + 8*self.square_size, y], width=self.grid_line_width)
        Color(*self.clear_color)

    def redraw_pieces(self, move, board=None, overlay=False, scale=1):
        if not self.square_size: # not recalc-ed yet
            return
        board = board or self.model
        scale=min(scale, 1)
        if not overlay:
            self.canvas.clear()
        with self.canvas:
            if move:
                self.highlight_move(move.uci())
            size = 2 * [self.square_size]
            for square, piece in board.piece_map().items():
                col, row = square % 8, square // 8
                xy = self.screen_coords(col, row)
                if overlay:
                    xy=[i+(1-scale)*j for i, j in zip(xy, size)]
                self.redraw_one_piece(piece, square, xy, [s * scale for s in size])

    def redraw_one_piece(self, piece, square, xy, size):
        Rectangle(pos=xy, size=size, texture=self.piece_texture(piece))

    def highlight_move(self, move):
        group = self.highlight if len(move) >= 4 else self.selection
        group.clear()
        w, h = 2*[self.square_size]
        for i, pos in enumerate([move[i:i+2] for i in range(0, min(4, len(move)), 2)]):
            x, y = [j for j in self.screen_coords(*pos)]
            self.highlight_pos = x+w/2, y+h/2
            self.highlight_area(group, i, x, y, w, h)
        if self.canvas.indexof(group) < 0:
            self.canvas.add(group)
        if group.children:
            group.add(Color(*self.clear_color))

    def screen_coords(self, col, row):
        assert self.square_size
        if isinstance(col, str):
            assert col in 'abcdefgh'    # expect file-rank
            assert int(row) in range(1, 9)
            col, row = 'abcdefgh'.index(col), int(row) - 1
        if self.flip:
            col = 7 - col
            row = 7 - row
        return [o + i * self.square_size for o, i in zip(self.xyo, [col, row])]

    def _square_name_from_coords(self, pos):
        x,y = [(i - j) / self.square_size for i, j in zip(pos, self.xyo)]
        if 0 <= x < 8 and 0 <= y < 8:
            x, y = int(x), int(y)
            if self.flip:
                x, y  = 7 - x, 7 - y
            return 'abcdefgh'[int(x)] + str(1 + int(y))
