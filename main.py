import os
# Web版の起動を安定させるための設定
os.environ['KIVY_NO_ARGS'] = '1'

import math
import random
import sys
import asyncio
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.properties import DictProperty, StringProperty, NumericProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.text import LabelBase, DEFAULT_FONT

# --- 環境判定 ---
IS_WEB = 'pygbag' in sys.modules

# --- 盤面座標データ ---
VALID_COORDS = [
    (2,0), (3,0), (4,0), (5,0), (2,7), (3,7), (4,7), (5,7),
    (1,1), (2,1), (3,1), (4,1), (5,1), (6,1), (1,6), (2,6), (3,6), (4,6), (5,6), (6,6),
    (0,2), (1,2), (2,2), (3,2), (4,2), (5,2), (6,2), (7,2),
    (0,3), (1,3), (2,3), (3,3), (4,3), (5,3), (6,3), (7,3),
    (0,4), (1,4), (2,4), (3,4), (4,4), (5,4), (6,4), (7,4),
    (0,5), (1,5), (2,5), (3,5), (4,5), (5,5), (6,5), (7,5),
]

CIRCUMFERENCE = [
    (0,3), (0,2), (1,1), (2,0), (3,0), (4,0), (5,0), (6,1), (7,2), (7,3),
    (7,4), (7,5), (6,6), (5,7), (4,7), (3,7), (2,7), (1,6), (0,5), (0,4)
]

class NipBoard(Widget):
    board_state = DictProperty({})
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw_board, size=self.draw_board, board_state=self.draw_board)

    def draw_board(self, *args):
        self.canvas.clear()
        padding = 110
        board_size = min(self.width, self.height) - padding
        cell_size = board_size / 7
        off_x = self.x + (self.width - board_size) / 2
        off_y = self.y + (self.height - board_size) / 2
        
        with self.canvas:
            Color(0.56, 0.74, 0.56, 1) 
            Rectangle(pos=self.pos, size=self.size)
            Color(0, 0, 0, 1)
            line_w = 1.2
            for c in VALID_COORDS:
                x1, y1 = off_x + c[0]*cell_size, off_y + c[1]*cell_size
                for dx, dy in [(1,0), (0,1), (1,1), (1,-1)]:
                    t = (c[0]+dx, c[1]+dy)
                    if t in VALID_COORDS:
                        x2, y2 = off_x + t[0]*cell_size, off_y + t[1]*cell_size
                        Line(points=[x1, y1, x2, y2], width=line_w)
            Line(circle=(self.center_x, self.center_y, cell_size * 3.8), width=line_w+0.5)
            for coord in VALID_COORDS:
                cx, cy = off_x + coord[0]*cell_size, off_y + coord[1]*cell_size
                stone = self.board_state.get(coord)
                if stone:
                    Color(0, 0, 0, 1) if stone == 'black' else Color(1, 1, 1, 1)
                    r = cell_size * 0.35
                    Ellipse(pos=(cx-r, cy-r), size=(r*2, r*2))
                    Color(0, 0, 0, 1)
                    Line(circle=(cx, cy, r), width=1)
                else:
                    Color(0.17, 0.24, 0.31, 1)
                    Rectangle(pos=(cx-2, cy-2), size=(4,4))

    def on_touch_down(self, touch):
        app = App.get_running_app()
        if app.turn == app.cpu_color and app.mode == "PvE": return
        padding = 110 
        board_size = min(self.width, self.height) - padding
        cell_size = board_size / 7
        off_x = self.x + (self.width - board_size) / 2
        off_y = self.y + (self.height - board_size) / 2
        for c in VALID_COORDS:
            tx, ty = off_x + c[0] * cell_size, off_y + c[1] * cell_size
            if Vector(touch.pos).distance(Vector(tx, ty)) < cell_size * 0.45:
                app.make_move_async(c)
                return True
        return super().on_touch_down(touch)

class MenuScreen(Screen):
    pass

class GameScreen(Screen):
    pass

class NipApp(App):
    board_state = DictProperty({})
    turn = StringProperty('black')
    status_text = StringProperty("")
    big_res_text = StringProperty("")
    
    def build(self):
        self.mode = "PvP"
        self.cpu_color = None
        self.cpu_level = 3
        self.history = []
        self.sm = ScreenManager()
        self.sm.add_widget(MenuScreen(name='menu'))
        self.sm.add_widget(GameScreen(name='game'))
        return self.sm

    def start_game(self, mode, cpu_side=None, level=3):
        self.mode = mode
        self.cpu_level = level
        self.cpu_color = 'black' if cpu_side == "先手" else 'white' if mode == "PvE" else None
        self.sm.current = 'game'
        self.reset_game()

    def reset_game(self):
        self.board_state = {coord: None for coord in VALID_COORDS}
        self.board_state[(3,3)] = self.board_state[(4,4)] = 'white'
        self.board_state[(4,3)] = self.board_state[(3,4)] = 'black'
        self.turn = 'black'
        self.history = []
        self.big_res_text = ""
        self.update_status()
        if self.mode == "PvE" and self.turn == self.cpu_color:
            asyncio.create_task(self.cpu_move_task())

    def update_status(self):
        b, w = list(self.board_state.values()).count('black'), list(self.board_state.values()).count('white')
        turn_str = 'B' if self.turn == 'black' else 'W'
        self.status_text = f"B: {b} W: {w} | Next: {turn_str} (Lv{self.cpu_level})"

    def get_flipped(self, start, color, board_state):
        if board_state.get(start) is not None: return []
        opp = 'white' if color == 'black' else 'black'
        normal_flipped = []
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            path, curr = [], (start[0]+dx, start[1]+dy)
            while curr in VALID_COORDS:
                st = board_state.get(curr)
                if st == opp: path.append(curr)
                elif st == color: normal_flipped.extend(path); break
                else: break
                curr = (curr[0]+dx, curr[1]+dy)
        circle_flipped = []
        if start in CIRCUMFERENCE:
            idx = CIRCUMFERENCE.index(start)
            circle = CIRCUMFERENCE[idx:] + CIRCUMFERENCE[:idx]
            for d in [1, -1]:
                path = []
                for i in range(1, len(circle)):
                    curr = circle[(i * d) % len(circle)]
                    st = board_state.get(curr)
                    if st == opp: path.append(curr)
                    elif st == color: circle_flipped.extend(path); break
                    else: break
        return list(set(normal_flipped + circle_flipped))

    def evaluate_board(self, board, color):
        score = 0
        for coord, st in board.items():
            if st is None: continue
            val = 15 if coord in CIRCUMFERENCE else 1
            score += val if st == color else -val
        return score

    def minimax(self, board, depth, alpha, beta, is_maximizing, color):
        opp = 'white' if color == 'black' else 'black'
        curr_p = color if is_maximizing else opp
        moves = [(n, self.get_flipped(n, curr_p, board)) for n in VALID_COORDS if self.get_flipped(n, curr_p, board)]
        if depth == 0 or not moves: return self.evaluate_board(board, color)
        v = -20000 if is_maximizing else 20000
        for move, flipped in moves:
            nb = board.copy()
            nb[move] = curr_p
            for f in flipped: nb[f] = curr_p
            res = self.minimax(nb, depth - 1, alpha, beta, not is_maximizing, color)
            if is_maximizing: v = max(v, res); alpha = max(alpha, v)
            else: v = min(v, res); beta = min(beta, v)
            if beta <= alpha: break
        return v

    async def cpu_move_task(self):
        await asyncio.sleep(0.6)
        moves = [(n, self.get_flipped(n, self.turn, self.board_state)) for n in VALID_COORDS if self.get_flipped(n, self.turn, self.board_state)]
        if not moves: return

        stone_count = sum(1 for v in self.board_state.values() if v is not None)
        empty_count = len(VALID_COORDS) - stone_count
        
        if self.turn == 'white' and stone_count == 5:
            best_m = random.choice(moves)[0]
        else:
            depth = {1: 0, 2: 1, 3: 2, 4: 2, 5: 3}[self.cpu_level]
            scored = []
            for m, f in moves:
                nb = self.board_state.copy(); nb[m] = self.turn
                for s in f: nb[s] = self.turn
                v = self.minimax(nb, depth, -20000, 20000, False, self.turn)
                scored.append((m, v))
            random.shuffle(scored)
            scored.sort(key=lambda x: x[1], reverse=True)
            
            if empty_count > 30 and random.random() < 0.30 and len(scored) > 1:
                top_k = min(3, len(scored))
                best_m = scored[random.randint(0, top_k-1)][0]
            else:
                best_m = scored[0][0]
        
        self.apply_move(best_m)

    def make_move_async(self, coord):
        # 重複呼び出しを避けるため、ここでは石を置く処理だけを呼ぶ
        self.apply_move(coord)

    def apply_move(self, coord):
        to_flip = self.get_flipped(coord, self.turn, self.board_state)
        if not to_flip: return False
        
        self.history.append({'board': self.board_state.copy(), 'turn': self.turn})
        new_board = self.board_state.copy()
        new_board[coord] = self.turn
        for n in to_flip: new_board[n] = self.turn
        self.board_state = new_board
        self.turn = 'white' if self.turn == 'black' else 'black'
        self.update_status()
        
        # 次のターン判定（CPU起動含む）をここから呼び出す
        asyncio.create_task(self.check_pass_task())
        return True

    async def check_pass_task(self):
        await asyncio.sleep(0.1)
        # 交代した後のプレイヤーが打てる手があるか確認
        moves = [n for n in VALID_COORDS if self.get_flipped(n, self.turn, self.board_state)]
        
        if not moves:
            # 打てないならパス
            opp = 'white' if self.turn == 'black' else 'black'
            # 相手も打てないなら終局
            if not [n for n in VALID_COORDS if self.get_flipped(n, opp, self.board_state)]:
                self.end_game()
            else:
                self.turn = opp # 再交代
                self.update_status()
                # パスしてCPUの番になった場合のみ動かす
                if self.mode == "PvE" and self.turn == self.cpu_color:
                    await self.cpu_move_task()
        else:
            # 打てる手があり、それがCPUの番なら動かす
            if self.mode == "PvE" and self.turn == self.cpu_color:
                await self.cpu_move_task()

    def undo(self):
        if not self.history: return
        self.big_res_text = ""
        if self.mode == "PvE":
            while self.history:
                s = self.history.pop()
                if s['turn'] != self.cpu_color:
                    self.board_state, self.turn = s['board'], s['turn']; break
        else:
            s = self.history.pop()
            self.board_state, self.turn = s['board'], s['turn']
        self.update_status()

    def end_game(self):
        b, w = list(self.board_state.values()).count('black'), list(self.board_state.values()).count('white')
        self.big_res_text = "DRAW" if b==w else ("BLACK WIN!" if b>w else "WHITE WIN!")

Builder.load_string('''
<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 50
        spacing: 20
        canvas.before:
            Color:
                rgba: 0.15, 0.2, 0.25, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "NIP STRATEGY"
            font_size: '30sp'
            bold: True
            size_hint_y: 0.2
        Button:
            text: "PLAYER vs PLAYER"
            size_hint_y: 0.15
            on_release: app.start_game("PvP")
        Label:
            text: "--- CPU SETTINGS ---"
            size_hint_y: 0.1
        BoxLayout:
            size_hint_y: 0.15
            spacing: 10
            ToggleButton:
                id: cpu_white
                text: "CPU: WHITE"
                group: 'side'
                state: 'down'
            ToggleButton:
                id: cpu_black
                text: "CPU: BLACK"
                group: 'side'
        BoxLayout:
            size_hint_y: 0.15
            spacing: 5
            ToggleButton:
                text: "Lv1"
                group: 'lv'
                id: lv1
            ToggleButton:
                text: "Lv2"
                group: 'lv'
                id: lv2
            ToggleButton:
                text: "Lv3"
                group: 'lv'
                id: lv3
                state: 'down'
            ToggleButton:
                text: "Lv4"
                group: 'lv'
                id: lv4
            ToggleButton:
                text: "Lv5"
                group: 'lv'
                id: lv5
        Button:
            text: "START GAME"
            size_hint_y: 0.2
            background_color: 0.5, 0.8, 1, 1
            on_release:
                side = "先手" if cpu_black.state == 'down' else "後手"
                level = 1 if lv1.state == 'down' else (2 if lv2.state == 'down' else (3 if lv3.state == 'down' else (4 if lv4.state == 'down' else 5)))
                app.start_game("PvE", side, level)

<GameScreen>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: 0.1
            Button:
                text: "UNDO"
                on_release: app.undo()
            Button:
                text: "MENU"
                on_release: app.sm.current = 'menu'
        NipBoard:
            board_state: app.board_state
            size_hint_y: 0.7
        Label:
            text: app.big_res_text
            font_size: '40sp'
            color: 1, 0, 0, 1
            size_hint_y: 0.12
            bold: True
        Label:
            text: app.status_text
            size_hint_y: 0.08
            bold: True
            font_size: '18sp'
''')

async def main():
    app = NipApp()
    # async_runを使用して、Kivyとasyncioのループを統合します
    await app.async_run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
