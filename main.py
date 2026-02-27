import sys
import asyncio
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window
from kivy.core.text import LabelBase, DEFAULT_FONT

# --------------------------------------------------
# 1. iOS(ブラウザ)版でも日本語を表示するためのフォント設定
# --------------------------------------------------
try:
    # ファイル名が 'font.ttc' だと読み込めないことがあるため、
    # もしブラウザ版で動かなければ、軽量な 'jp.ttf' などに変更してください。
    LabelBase.register(DEFAULT_FONT, "font.ttc")
except Exception as e:
    print(f"Font registration failed: {e}")

# --------------------------------------------------
# 2. ゲームのロジックとUI
# --------------------------------------------------
class NipGrid(GridLayout):
    def __init__(self, **kwargs):
        super(NipGrid, self).__init__(**kwargs)
        self.cols = 8  # 8x8の盤面
        # 修正ポイント①: Androidで角が切れないよう、盤面の周りに余白（パディング）を追加
        self.padding = [20, 20, 20, 20] # [左, 上, 右, 下]
        self.spacing = 2
        
        # 盤面の状態（0:空, 1:黒, 2:白）
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        
        # 初期配置
        self.board[3][3] = 2
        self.board[3][4] = 1
        self.board[4][3] = 1
        self.board[4][4] = 2
        
        self.create_board()
        self.current_player = 1 # 1:黒, 2:白

    def create_board(self):
        for r in range(8):
            for c in range(8):
                btn = Button(background_color=(0, 0.5, 0, 1)) # 緑色のマス
                btn.bind(on_release=self.on_click)
                btn.r = r
                btn.c = c
                self.add_widget(btn)
                self.buttons[r][c] = btn
                self.update_marker(r, c)

    def update_marker(self, r, c):
        # 石（マーカー）を描画
        btn = self.buttons[r][c]
        btn.canvas.after.clear()
        with btn.canvas.after:
            if self.board[r][c] == 1: # 黒石
                Color(0, 0, 0, 1)
                Ellipse(pos=(btn.pos[0]+5, btn.pos[1]+5), size=(btn.size[0]-10, btn.size[1]-10))
            elif self.board[r][c] == 2: # 白石
                Color(1, 1, 1, 1)
                Ellipse(pos=(btn.pos[0]+5, btn.pos[1]+5), size=(btn.size[0]-10, btn.size[1]-10))

    def on_click(self, btn):
        # (ここにオセロのひっくり返すロジックなどを実装)
        # 今回は、クリックした場所の色が変わるだけの簡易実装とします
        r, c = btn.r, btn.c
        if self.board[r][c] == 0:
            self.board[r][c] = self.current_player
            self.update_marker(r, c)
            # プレイヤー交代
            self.current_player = 2 if self.current_player == 1 else 1
            
            # (勝ち負け判定ロジック)
            # 簡易的に、盤面がすべて埋まったら終了とします
            if all(self.board[r][c] != 0 for r in range(8) for c in range(8)):
                # 修正ポイント②: 終了メッセージを大きい文字にする関数を呼び出す
                App.get_running_app().root.show_end_message("終了！黒：32　白：32　引き分け！")

class NipApp(App):
    def build(self):
        # 修正ポイント③: 終了メッセージを表示するためのLabelを追加
        self.end_label = Label(text="", font_size='60sp', color=(1, 0, 0, 1), size_hint_y=None, height=100) # 文字サイズを3倍('60sp'), 赤色
        
        # メインのレイアウト（上：盤面、下：メッセージ）
        root = BoxLayout(orientation='vertical')
        
        self.grid = NipGrid()
        self.status_label = Label(text="黒の番です", font_size='20sp', size_hint_y=None, height=50) # 今のメッセージ
        
        root.add_widget(self.grid) # 上に盤面
        root.add_widget(self.end_label) # 修正ポイント④: 盤面と今のメッセージの間に、大きい終了メッセージ用のラベルを追加
        root.add_widget(self.status_label) # 下に今のメッセージ
        return root

    def show_end_message(self, message):
        # 修正ポイント⑤: 勝ち負けが決まった時に、大きい文字でメッセージを表示
        self.end_label.text = message
        self.status_label.text = "ゲーム終了"

# --------------------------------------------------
# 3. Android/iOS(ブラウザ) 両対応のための起動コード
# --------------------------------------------------
if __name__ == '__main__':
    # ブラウザ版（Pygbag）の場合
    if 'pygbag' in sys.modules:
        async def main():
            await NipApp().async_run()
        asyncio.run(main())
    # Android版やPC版の場合
    else:
        NipApp().run()
