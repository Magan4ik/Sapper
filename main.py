from math import *
import pyglet
from pyglet.window import key, mouse, FPSDisplay
from pyglet import shapes

from settings import *
from Objects import *

if __name__ == '__main__': # Основний блок ініціалізації
    win = pyglet.window.Window(W, H + 50, style = pyglet.window.Window.WINDOW_STYLE_DEFAULT, caption = 'Sapper') # Створюємо вікно
    ui = UI()
    game = GameProcesses()
    ui.menu()
    ui.create_game_net()
    ui.create_score_text()

def start(): # Починаємо та ініціалізуємо гру
    game.start = True
    game.game_over = False
    amount = game.undermine(game.diff)
    ui.change_score(amount)

@win.event # Обробка натиску кнопки миші
def on_mouse_press(x, y, but, mod):
    if not game.game_over and game.start: # Якщо гра не закінчена
        if but == mouse.LEFT:
            kx = x // SIZE
            ky = y // SIZE
            game.check(kx, ky) # Розкриття клітинки

        elif but == mouse.RIGHT:
            kx = x // SIZE
            ky = y // SIZE
            flag = game.set_flag(kx, ky) # Встановлення прапорця

            if flag == 'sub': # Змінюємо рахунок
                ui.change_score(ui - 1)
                if ui.score == 0:
                    if game.mines == game.right_flags: #
                        game.winning()
            elif flag == 'add':
                ui.change_score(ui + 1)

    if not game.start: # Обов'язково після обробки інших кнопок
        if but == mouse.LEFT:
            p = ui.butt.press(x, y) # Перевірка натиску кнопки
            if p:
                start()
    if game.game_over:
        p = game.retry_butt.press(x, y) # Якщо натиснута кропка заново
        if p:
            game.start = False


@win.event # Обробка переміщення нажатої миші
def on_mouse_drag(x, y, dx, dy, but, mod):
    if not game.start:
        game.diff = ui.scroller.drag(x, y, dx) # Переміщення ползунка

@win.event # Відмальовування
def on_draw():
    win.clear()
    if game.start:
        shapes.Rectangle(0, 0, width = W, height = H, color = BACKGROUND).draw() # Малювання фону
        game.draw()
        ui.draw()
        if game.game_over:
            game.background.draw() # Малювання кінця гри
            game.retry_butt.todraw()
    else:
        ui.background.draw() # Малювання доігрового меню
        ui.butt.todraw()
        ui.scroller.todraw()
        ui.text.draw()


pyglet.app.run()
