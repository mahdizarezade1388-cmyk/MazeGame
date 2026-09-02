import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.clock import Clock

class MazeWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.draw_game, pos=self.draw_game)
        self.player_color = (0, 0.9, 0.46, 1)
        self.wall_color = (0, 0.69, 1, 1)
        self.finish_color = (1, 0.32, 0.32, 1)
        self.bg_color = (0.07, 0.07, 0.07, 1)
        
        self.current_level = 1
        self.max_unlocked_level = 1
        self.stones = set()
        self.player_x = 1
        self.player_y = 1
        self.finish_x = 1
        self.finish_y = 1
        self.cols = 5
        self.rows = 5
        self.is_game_over = False

    def setup_level(self, level):
        self.current_level = level
        self.is_game_over = False
        
        self.size_cell = max(20, int(60 - (self.current_level - 1) * 2))
        self.cols = int(self.width // self.size_cell) // 2 * 2 + 1
        self.rows = int(self.height // self.size_cell) // 2 * 2 + 1
        if self.cols < 3: self.cols = 3
        if self.rows < 3: self.rows = 3

        grid = [[1 for _ in range(self.cols)] for _ in range(self.rows)]

        def carve_passages(cx, cy):
            grid[cy][cx] = 0
            dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
            random.seed(self.current_level * 100 + cx * cy)
            random.shuffle(dirs)
            for dx, dy in dirs:
                nx, ny = cx + dx, cy + dy
                if 0 < nx < self.cols - 1 and 0 < ny < self.rows - 1 and grid[ny][nx] == 1:
                    grid[cy + dy // 2][cx + dx // 2] = 0
                    carve_passages(nx, ny)

        carve_passages(1, 1)

        self.stones = set()
        for r in range(self.rows):
            for c in range(self.cols):
                if grid[r][c] == 1:
                    if self.current_level <= 3 and (c + r) % 2 == 0: continue
                    if self.current_level <= 6 and (c * r) % 5 == 0: continue
                    self.stones.add((c, r))

        self.player_x, self.player_y = 1, 1
        self.finish_x, self.finish_y = self.cols - 2, self.rows - 2

        self.stones.discard((self.player_x, self.player_y))
        self.stones.discard((self.finish_x, self.finish_y))
        self.draw_game()

    def draw_game(self, *args):
        self.canvas.clear()
        if not hasattr(self, 'size_cell') or self.size_cell <= 0:
            return

        with self.canvas:
            Color(*self.bg_color)
            Rectangle(pos=self.pos, size=self.size)

            Color(*self.wall_color)
            for cx, cy in self.stones:
                Rectangle(
                    pos=(self.x + cx * self.size_cell, self.y + cy * self.size_cell),
                    size=(self.size_cell, self.size_cell)
                )

            Color(*self.finish_color)
            Rectangle(
                pos=(self.x + self.finish_x * self.size_cell + 2, self.y + self.finish_y * self.size_cell + 2),
                size=(self.size_cell - 4, self.size_cell - 4)
            )

            Color(*self.player_color)
            Ellipse(
                pos=(self.x + self.player_x * self.size_cell + 3, self.y + self.player_y * self.size_cell + 3),
                size=(self.size_cell - 6, self.size_cell - 6)
            )

    def move_player(self, dx, dy):
        if self.is_game_over:
            return

        new_x = self.player_x + dx
        new_y = self.player_y + dy

        if (new_x < 0 or new_x >= self.cols or 
            new_y < 0 or new_y >= self.rows or 
            (new_x, new_y) in self.stones):
            return

        self.player_x = new_x
        self.player_y = new_y
        self.draw_game()

        if self.player_x == self.finish_x and self.player_y == self.finish_y:
            self.complete_level()

    def complete_level(self):
        self.is_game_over = True
        if self.current_level >= self.max_unlocked_level and self.max_unlocked_level < 20:
            self.max_unlocked_level = self.current_level + 1
        
        if self.current_level < 20:
            Clock.schedule_once(lambda dt: self.setup_level(self.current_level + 1), 0.5)

class MainGameApp(App):
    def build(self):
        self.root_layout = BoxLayout(orientation='vertical')
        
        # بخش بالای صفحه
        self.top_bar = BoxLayout(size_hint_y=0.1, padding=10)
        self.info_label = Label(text="Level 1 / 20", font_size='20sp', bold=True)
        self.top_bar.add_widget(self.info_label)
        self.root_layout.add_widget(self.top_bar)

        # بوم بازی
        self.maze_widget = MazeWidget(size_hint_y=0.55)
        self.root_layout.add_widget(self.maze_widget)

        # دکمه‌های کنترلی با چیدمان ۳ در ۳ بعلاوه‌ای (مرکز خالی)
        controls = GridLayout(cols=3, rows=3, size_hint_y=0.35, padding=10, spacing=5)
        
        btn_up = Button(text="^", font_size='30sp', bold=True, on_press=lambda x: self.move(0, 1))
        btn_down = Button(text="v", font_size='25sp', bold=True, on_press=lambda x: self.move(0, -1))
        btn_left = Button(text="<", font_size='30sp', bold=True, on_press=lambda x: self.move(-1, 0))
        btn_right = Button(text=">", font_size='30sp', bold=True, on_press=lambda x: self.move(1, 0))

        # ردیف ۱: [خالی، بالا، خالی]
        controls.add_widget(Widget())
        controls.add_widget(btn_up)
        controls.add_widget(Widget())
        
        # ردیف ۲: [چپ، خالی، راست]
        controls.add_widget(btn_left)
        controls.add_widget(Widget())
        controls.add_widget(btn_right)

        # ردیف ۳: [خالی، پایین، خالی]
        controls.add_widget(Widget())
        controls.add_widget(btn_down)
        controls.add_widget(Widget())

        self.root_layout.add_widget(controls)
        
        Clock.schedule_once(self.init_game, 0.1)
        return self.root_layout

    def init_game(self, dt):
        self.maze_widget.setup_level(1)

    def move(self, dx, dy):
        self.maze_widget.move_player(dx, dy)
        self.info_label.text = f"Level {self.maze_widget.current_level} / 20"

if __name__ == '__main__':
    MainGameApp().run()