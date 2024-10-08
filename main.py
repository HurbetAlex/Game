import tkinter as tk
import random
import pygame
import math
from PIL import ImageTk, Image
import json

class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Игровое приложение")
        self.root.geometry("800x600")
        self.game_running = False
        self.difficulty = "Легкий"
        self.high_scores = []
        self.language = 'ru'

        pygame.mixer.init()

        self.translations = {
            'ru': {
                'select_difficulty': 'Выберите уровень сложности',
                'easy': 'Легкий',
                'medium': 'Средний',
                'hard': 'Тяжелый',
                'exit': 'Выход',
                'view_scores': 'Посмотреть таблицу рекордов',
                'pause': 'Пауза',
                'resume': 'Продолжить',
                'game_over': 'Игра окончена!',
                'main_menu': 'Главное меню',
                'high_scores': 'Таблица рекордов',
                'no_scores': 'Пока нет рекордов.',
                'back': 'Назад',
                'difficulty': 'Сложность',
                'settings': 'Настройки',
                'start_game': 'Начать игру',
                'lives': 'Жизни',
                'level': 'Уровень',
                'score': 'Очки',
                'time': 'Время',
                'language': 'Язык',
                'save': 'Сохранить',
                'load': 'Загрузить',
                'sound': 'Звук',
                'on': 'Вкл',
                'off': 'Выкл',
            }
        }

        self.t = self.translations[self.language]

        self.sound_on = True

        self.create_main_menu()

    def create_main_menu(self):
        self.stop_game()
        self.clear_screen()

        title_label = tk.Label(self.root, text=self.t['select_difficulty'], font=('Arial', 24))
        title_label.pack(pady=20)

        easy_button = tk.Button(self.root, text=self.t['easy'], command=lambda: self.start_game("Легкий"))
        easy_button.pack(pady=10)

        medium_button = tk.Button(self.root, text=self.t['medium'], command=lambda: self.start_game("Средний"))
        medium_button.pack(pady=10)

        hard_button = tk.Button(self.root, text=self.t['hard'], command=lambda: self.start_game("Тяжелый"))
        hard_button.pack(pady=10)

        settings_button = tk.Button(self.root, text=self.t['settings'], command=self.open_settings)
        settings_button.pack(pady=10)

        scores_button = tk.Button(self.root, text=self.t['view_scores'], command=self.show_high_scores)
        scores_button.pack(pady=10)

        exit_button = tk.Button(self.root, text=self.t['exit'], command=self.root.quit)
        exit_button.pack(pady=20)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def start_game(self, difficulty):
        self.difficulty = difficulty
        self.clear_screen()

        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_running = True
        self.bonuses = []
        self.time_left = 60

        if self.difficulty == "Легкий":
            self.obstacle_speed = 2
            self.collectibles_count = 3
        elif self.difficulty == "Средний":
            self.obstacle_speed = 4
            self.collectibles_count = 5
        elif self.difficulty == "Тяжелый":
            self.obstacle_speed = 6
            self.collectibles_count = 7

        self.create_widgets()
        self.create_canvas()
        self.bind_keys()
        self.create_obstacles()
        self.create_collectibles()
        self.update_score()
        self.create_timer_label()
        self.update_timer()
        self.play_background_music()
        self.schedule_bonus()

        self.update_game()

    def create_widgets(self):
        self.pause_button = tk.Button(self.root, text=self.t['pause'], command=self.pause_game)
        self.pause_button.pack(pady=10)

        exit_button = tk.Button(self.root, text=self.t['exit'], command=self.exit_to_main_menu)
        exit_button.pack(pady=10)

    def create_canvas(self):
        self.canvas = tk.Canvas(self.root, width=600, height=400, bg="lightblue")
        self.canvas.pack(pady=20)

        self.player_image = Image.open("player.png")
        self.player_image = self.player_image.resize((50, 50))
        self.player_image = ImageTk.PhotoImage(self.player_image)
        self.player = self.canvas.create_image(75, 75, image=self.player_image)

        self.score_label = tk.Label(self.root, text="", font=('Arial', 16))
        self.score_label.pack()

    def bind_keys(self):
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        self.root.bind("<Up>", self.move_up)
        self.root.bind("<Down>", self.move_down)

    def create_obstacles(self):
        self.obstacles = []
        for _ in range(5 + self.level * 2):
            x1 = random.randint(100, 500)
            y1 = random.randint(100, 300)
            x2 = x1 + 50
            y2 = y1 + 50
            obstacle_type = random.choice(['normal', 'chasing'])
            if obstacle_type == 'chasing':
                obstacle = self.canvas.create_rectangle(x1, y1, x2, y2, fill='black')
                self.obstacles.append([obstacle, 'chasing'])
            else:
                obstacle = self.canvas.create_rectangle(x1, y1, x2, y2, fill='blue')
                dx = random.choice([-self.obstacle_speed, self.obstacle_speed])
                dy = random.choice([-self.obstacle_speed, self.obstacle_speed])
                self.obstacles.append([obstacle, dx, dy])

    def create_collectibles(self):
        self.collectibles = []
        for _ in range(self.collectibles_count + self.level):
            x = random.randint(100, 500)
            y = random.randint(100, 300)
            collectible_image = Image.open("collect.png")
            collectible_image = collectible_image.resize((30, 30))
            collectible_image = ImageTk.PhotoImage(collectible_image)
            collectible = self.canvas.create_image(x, y, image=collectible_image)
            self.collectibles.append({'id': collectible, 'image': collectible_image})

    def update_score(self):
        self.score_label.config(
            text=f"{self.t['score']}: {self.score}  |  {self.t['level']}: {self.level}  |  {self.t['lives']}: {self.lives}  |  {self.t['difficulty']}: {self.difficulty}")

    def update_timer(self):
        if self.game_running and self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"{self.t['time']}: {self.time_left}s")
            self.root.after(1000, self.update_timer)
        elif self.time_left == 0:
            self.end_game()

    def create_timer_label(self):
        self.timer_label = tk.Label(self.root, text=f"{self.t['time']}: {self.time_left}s", font=('Arial', 16))
        self.timer_label.pack()

    def update_game(self):
        if self.game_running and self.canvas.winfo_exists():
            for obstacle_data in self.obstacles:
                obstacle = obstacle_data[0]
                if obstacle_data[1] == 'chasing':
                    self.move_towards_player(obstacle)
                else:
                    dx, dy = obstacle_data[1], obstacle_data[2]
                    self.canvas.move(obstacle, dx, dy)
                    obstacle_coords = self.canvas.coords(obstacle)
                    if obstacle_coords[0] <= 0 or obstacle_coords[2] >= 600:
                        dx *= -1
                    if obstacle_coords[1] <= 0 or obstacle_coords[3] >= 400:
                        dy *= -1
                    obstacle_data[1], obstacle_data[2] = dx, dy
            self.check_collision()
            self.root.after(100, self.update_game)
        else:
            self.game_running = False

    def pause_game(self):
        self.game_running = not self.game_running
        if self.game_running:
            self.pause_button.config(text=self.t['pause'])
            self.update_game()
            pygame.mixer.music.unpause()
        else:
            self.pause_button.config(text=self.t['resume'])
            pygame.mixer.music.pause()

    def move_left(self, event):
        if self.canvas.winfo_exists():
            self.canvas.move(self.player, -20, 0)
            self.check_collision()

    def move_right(self, event):
        if self.canvas.winfo_exists():
            self.canvas.move(self.player, 20, 0)
            self.check_collision()

    def move_up(self, event):
        if self.canvas.winfo_exists():
            self.canvas.move(self.player, 0, -20)
            self.check_collision()

    def move_down(self, event):
        if self.canvas.winfo_exists():
            self.canvas.move(self.player, 0, 20)
            self.check_collision()

    def check_collision(self):
        if not self.canvas.winfo_exists():
            return
        player_coords = self.canvas.bbox(self.player)

        for obstacle_data in self.obstacles:
            obstacle = obstacle_data[0]
            if self.is_collision(player_coords, self.canvas.bbox(obstacle)):
                self.lives -= 1
                self.update_score()
                if self.lives <= 0:
                    self.end_game()
                else:
                    self.canvas.coords(self.player, 75, 75)
                    self.play_sound('collision.wav')

        for collectible in self.collectibles[:]:
            if self.is_collision(player_coords, self.canvas.bbox(collectible['id'])):
                self.play_sound('collect.wav')
                self.canvas.delete(collectible['id'])
                self.collectibles.remove(collectible)
                self.score += 10
                self.update_score()
                if len(self.collectibles) == 0:
                    self.level_up()

        for bonus in self.bonuses[:]:
            if self.is_collision(player_coords, self.canvas.bbox(bonus['id'])):
                self.play_sound('bonus.wav')
                self.canvas.delete(bonus['id'])
                self.bonuses.remove(bonus)
                self.score += 50
                self.update_score()

    def is_collision(self, coords1, coords2):
        x1, y1, x2, y2 = coords1
        ox1, oy1, ox2, oy2 = coords2
        return not (x2 < ox1 or x1 > ox2 or y2 < oy1 or y1 > oy2)

    def end_game(self):
        pygame.mixer.music.stop()
        self.play_sound('game_over.wav')
        self.stop_game()
        self.canvas.create_text(300, 200, text=self.t['game_over'], font=('Arial', 24), fill="red")
        self.update_high_scores()

    def level_up(self):
        self.level += 1
        self.create_obstacles()
        self.create_collectibles()
        self.update_score()

    def stop_game(self):
        self.game_running = False
        self.root.unbind("<Left>")
        self.root.unbind("<Right>")
        self.root.unbind("<Up>")
        self.root.unbind("<Down>")

    def move_towards_player(self, obstacle):
        obstacle_coords = self.canvas.coords(obstacle)
        player_coords = self.canvas.coords(self.player)
        dx = player_coords[0] - obstacle_coords[0]
        dy = player_coords[1] - obstacle_coords[1]
        distance = math.hypot(dx, dy)
        if distance != 0:
            dx /= distance
            dy /= distance
            speed = self.obstacle_speed
            self.canvas.move(obstacle, dx * speed, dy * speed)

    def update_high_scores(self):
        self.high_scores.append(self.score)
        self.high_scores.sort(reverse=True)
        if len(self.high_scores) > 5:
            self.high_scores = self.high_scores[:5]
        self.save_high_scores()
        self.show_high_scores()

    def save_high_scores(self):
        with open('high_scores.json', 'w') as f:
            json.dump(self.high_scores, f)

    def load_high_scores(self):
        try:
            with open('high_scores.json', 'r') as f:
                self.high_scores = json.load(f)
        except FileNotFoundError:
            self.high_scores = []

    def show_high_scores(self):
        self.stop_game()
        self.clear_screen()

        title = tk.Label(self.root, text=self.t['high_scores'], font=('Arial', 24))
        title.pack(pady=20)

        if not self.high_scores:
            no_scores = tk.Label(self.root, text=self.t['no_scores'], font=('Arial', 16))
            no_scores.pack(pady=10)
        else:
            for index, score in enumerate(self.high_scores, start=1):
                score_label = tk.Label(self.root, text=f"{index}. {score} {self.t['score']}", font=('Arial', 16))
                score_label.pack(pady=5)

        back_button = tk.Button(self.root, text=self.t['back'], command=self.create_main_menu)
        back_button.pack(pady=20)

    def play_sound(self, sound_file):
        if self.sound_on:
            sound = pygame.mixer.Sound(sound_file)
            sound.play()

    def play_background_music(self):
        if self.sound_on:
            pygame.mixer.music.load('background_music.mp3')
            pygame.mixer.music.play(-1)

    def create_bonus(self):
        x = random.randint(100, 500)
        y = random.randint(100, 300)
        bonus_image = Image.open("bonus.png")
        bonus_image = bonus_image.resize((40, 40))
        bonus_image = ImageTk.PhotoImage(bonus_image)
        bonus = self.canvas.create_image(x, y, image=bonus_image)
        self.bonuses.append({'id': bonus, 'image': bonus_image})
        self.root.after(5000, lambda: self.remove_bonus(bonus))

    def remove_bonus(self, bonus_id):
        for bonus in self.bonuses:
            if bonus['id'] == bonus_id:
                self.canvas.delete(bonus_id)
                self.bonuses.remove(bonus)
                break

    def schedule_bonus(self):
        if self.game_running:
            self.create_bonus()
            self.root.after(random.randint(10000, 20000), self.schedule_bonus)

    def exit_to_main_menu(self):
        pygame.mixer.music.stop()
        self.create_main_menu()

    def open_settings(self):
        self.clear_screen()

        title_label = tk.Label(self.root, text=self.t['settings'], font=('Arial', 24))
        title_label.pack(pady=20)

        language_label = tk.Label(self.root, text=self.t['language'], font=('Arial', 16))
        language_label.pack(pady=5)

        language_var = tk.StringVar(value=self.language)
        language_menu = tk.OptionMenu(self.root, language_var, *self.translations.keys())
        language_menu.pack(pady=5)

        sound_label = tk.Label(self.root, text=self.t['sound'], font=('Arial', 16))
        sound_label.pack(pady=5)

        sound_var = tk.BooleanVar(value=self.sound_on)
        sound_checkbox = tk.Checkbutton(self.root, text=self.t['on'] if self.sound_on else self.t['off'],
                                        variable=sound_var, command=lambda: self.toggle_sound(sound_var))
        sound_checkbox.pack(pady=5)

        save_button = tk.Button(self.root, text=self.t['save'], command=lambda: self.save_settings(language_var.get()))
        save_button.pack(pady=20)

        back_button = tk.Button(self.root, text=self.t['back'], command=self.create_main_menu)
        back_button.pack(pady=10)

    def toggle_sound(self, sound_var):
        self.sound_on = sound_var.get()

    def save_settings(self, selected_language):
        self.language = selected_language
        self.t = self.translations[self.language]
        self.create_main_menu()

    def save_game(self):
        game_state = {
            'score': self.score,
            'level': self.level,
            'lives': self.lives,
            'difficulty': self.difficulty,
            'time_left': self.time_left
        }
        with open('savegame.json', 'w') as f:
            json.dump(game_state, f)

    def load_game(self):
        try:
            with open('savegame.json', 'r') as f:
                game_state = json.load(f)
            self.score = game_state['score']
            self.level = game_state['level']
            self.lives = game_state['lives']
            self.difficulty = game_state['difficulty']
            self.time_left = game_state['time_left']
            self.start_game(self.difficulty)
        except FileNotFoundError:
            pass

    def show_tutorial(self):
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    app.load_high_scores()
    root.mainloop()
