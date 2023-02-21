import random
import pyglet
from pyglet.window import key, mouse, FPSDisplay
from pyglet import shapes

import numpy as np

from settings import *
import time



class Mine(shapes.Rectangle): # Клас міни(унаслідуємо клас прямокутника)
    def __init__(self, kx, ky):
        self.kx = kx
        self.ky = ky
        x = kx * SIZE
        y = ky * SIZE
        width = SIZE
        height = SIZE
        color = (150, 50, 50)
        super().__init__(x, y, width, height, color, batch = None)
        self.hide = True

    def disclosure(self): # Розкриття міни
        self.hide = False

class Flag(shapes.Rectangle): # Клас прапорця(унаслідуємо клас прямокутника)
    def __init__(self, kx, ky):
        self.kx = kx
        self.ky = ky
        x = (kx * SIZE) + SIZE / 3
        y = (ky * SIZE) + SIZE / 3
        width = FLAG_SIZE
        height = FLAG_SIZE
        color = (50, 150, 50)
        super().__init__(x, y, width, height, color)

class Number(pyglet.text.Label):
    def __init__(self, kx, ky, num):
        x = (kx * SIZE) + SIZE / 2
        y = (ky * SIZE) + SIZE / 2
        self.num = str(num)
        super().__init__(str(num),
                        font_name = 'Comic Sans MC',
                        font_size = SIZE / 1.5,
                        x = x, y = y,
                        anchor_x = 'center', anchor_y = 'center')

        self.hide = True

    def change_num(self, new):
        self.num = str(new)
        self.text = str(new)

    def disclosure(self): # Розкриття цифри
        self.hide = False

    def __add__(self, other): # Метод який дозволяє нам використовувати "+" для класа
        return int(self.text) + int(other)

class EmptyCell(shapes.Rectangle): # Класс порожньої клітинки
    def __init__(self, kx, ky):
        self.kx = kx
        self.ky = ky
        x = kx * SIZE
        y = ky * SIZE
        width = SIZE
        height = SIZE
        color = (75, 75, 75)
        super().__init__(x, y, width, height, color, batch = None)
        self.hide = False

    def disclosure(self): # Розкриття клітинки
        self.hide = False

class Scroller: # Клас повзунка для вибору складності
    def __init__(self, x, y, start, end, step, step_width, batch = None):
        self.step_width = step_width
        self.step = step
        self.width = step_width * ( (end - start) / step)
        self.height = 2
        self.color = (200, 200, 200)
        #V Лінія повзунка V#
        self.rect = shapes.Rectangle(x, y, self.width, self.height, color = self.color, batch = batch)
        self.width2 = step_width / 3
        self.x = x - self.width2 / 2
        self.height2 = step_width / 2
        self.y = y - self.height2 / 3
        #V Вказівник повнузка V#
        self.pointer = shapes.Rectangle(self.x, self.y,
                                        self.width2, self.height2, color = self.color,
                                        batch = batch)
        #V Лічільник повзунка V#
        self.count = pyglet.text.Label(
                            '0',
                            font_name = 'Comic Sans MC',
                            font_size = SIZE / 1.5,
                            x = x + self.width / 2, y = y + self.height2 * 2,
                            anchor_x = 'center', anchor_y = 'center',
                            batch = batch)
    def drag(self, x, y, dx): # Ф-я переміщення вказівника
        if x in range(int(self.rect.x) - 20, int(self.rect.x + self.width) + 20):
            if y in range(int(self.pointer.y - 10), int(self.pointer.y + self.height2 + 10)):

                self.pointer.x += dx
                # Границі
                if self.pointer.x < self.x:
                    self.pointer.x = self.x

                if self.pointer.x > self.rect.x + self.width:
                    self.pointer.x = self.rect.x + self.width
        #V Значення повзунка V#
        new = int(((self.pointer.x - self.x) / self.step_width) * self.step)
        self.counter(new)
        return new

    def counter(self, new): # Зміна лічільника
        self.count.text = str(new)

    def todraw(self): # Відмальовування повзунка
        self.rect.draw()
        self.pointer.draw()
        self.count.draw()

class Button(shapes.Rectangle): # Клас кнопки
    def __init__(self, x, y, w, h, color, label, batch = None):
        super().__init__(x, y, w, h, color = color, batch = batch) # Кнопка
        #V Налаштування тексту V#
        self.label = label
        self.label.x = self.x + self.width / 2
        self.label.y = self.y + self.height / 2
        self.label.batch = batch
    def press(self, x, y): # Перевірка на натиск
        if x in range(int(self.x), int(self.x + self.width)) and\
        y in range(int(self.y), int(self.y + self.height)):
            return True
        else:
            return False

    def todraw(self): # Відмальовування кнопки
        self.draw()
        self.label.draw()

def check_around_cell(i, j): # Ф-я яка перебирає клітинки навколо заданої і повертає генератор із значень індексів
    for row in range(i - 1, i + 2, 1):
        if row == -1: continue
        if row == MAP_SIZE[0]: continue
        for col in range(j - 1, j + 2, 1):
            if col == -1: continue
            if col == MAP_SIZE[1]: continue

            if row == i and col == j: continue

            yield row, col

def create_matrix_mines(diff): # Ф-я для створення матриці нашего ігрового поля
    if diff == 0: diff = 1
    amont_mines = (diff / 100) * (MAP_SIZE[0]*MAP_SIZE[1]) # Створюємо к-ть мін згідно складності diff
    num = random.randint(int(0.9*amont_mines), int(1.1*amont_mines)) # Робимо невиликий розкид diff +- 10%
    matrix = [[Number(i, j, 0) for i in range(MAP_SIZE[0])] for j in range(MAP_SIZE[1])] # Наша порожня матриця
    #V Перетворюємо матрицю в об'єкт numpy для транспонування V#
    matrix = np.array(matrix).T
    n = 0
    while n < num: # Цикл додавання мін у матрицю(додаємо міни у випадкові координати)
        i = random.randint(0, MAP_SIZE[0] - 1)
        j = random.randint(0, MAP_SIZE[1] - 1)

        if type(matrix[i][j]).__name__ == 'Number': # Перевіряємо чи там текст
            matrix[i][j] = Mine(i, j) # Занесення у клітинку міну

            for row, col in check_around_cell(i, j):
                if type(matrix[row][col]).__name__ == 'Number': # Перевіряємо чи там текст і якщо так, то додаємо 1
                    matrix[row][col].change_num(matrix[row][col] + 1)
        else:
            continue
        n += 1


    return matrix, num


class GameProcesses: # Клас з ігровими процесами(замінування, перевірка, встановлення прапорця...)
    def __init__(self):
        self.start = False
        self.field_batch = pyglet.graphics.Batch()
        self.game_over = False
        self.over_batch = pyglet.graphics.Batch()
        self.mines = 0
        self.diff = 0

    def undermine(self, difficult): # Процес замінування
        self.empty_cells = []
        #V Створюємо нульову матрицю в numpy для транспонування. Вказуємо тип данних об'єкт, бо потім будемо пихати туди Flag V#
        self.flags_matrix = np.zeros((MAP_SIZE[1], MAP_SIZE[0]), dtype = 'object_').T
        self.field, amount = create_matrix_mines(difficult)
        self.mines = amount
        self.right_flags = 0
        return amount

    def check(self, kx, ky): # Ф-я розкриття клітинки
        flag = self.flags_matrix[ky][kx]
        obj = self.field[kx][ky]
        if not flag: # Не можна розкрити клітинку якщо там флаг

            #V Якщо ми натиснули на число поруч з яким потрібна к-ть прапорців - розкриваємо все навколо V#
            if type(obj).__name__ == 'Number' and obj.text != '0' and not obj.hide:
                flags = 0
                for row, col in check_around_cell(ky, kx): # Рахуємо прапорці поруч
                    if self.flags_matrix[row][col] != 0:
                        flags += 1

                if flags == int(obj.text):
                    for row, col in check_around_cell(kx, ky):
                        if self.field[row][col].hide:
                            self.check(row, col)

            self.field[kx][ky].disclosure() # Розкриття клітинки
            if type(obj).__name__ == 'Mine': # Якщо ми розкрили міну - програємо
                self.losing()
                return ...

            #V Якщо клітинка '0', то робимо її пустою та розкриваємо клітинки навколо V#
            if type(obj).__name__ == 'Number' and obj.text == '0':
                self.empty_cells.append(EmptyCell(kx, ky))

                for row, col in check_around_cell(kx, ky):
                    if self.field[row][col].hide:
                        self.check(row, col)


    def set_flag(self, kx, ky): # Ф-я встановлення прапорця
        if self.field[kx][ky].hide:
            if self.flags_matrix[ky][kx] == 0: # Якщо прапорця тут немає - встановлюємо
                self.flags_matrix[ky][kx] = Flag(kx, ky)
                if type(self.field[kx][ky]).__name__ == 'Mine': # Якщо прапорець поставлен вірно - дадаємо до змінної
                    self.right_flags += 1
                return 'sub' # Якщо флаг встановлено
            else: # Якщо він є - видаляємо
                self.flags_matrix[ky][kx] = 0
                if type(self.field[kx][ky]).__name__ == 'Mine': # Якщо прапорець знят невірно - відниміємо від змінної
                    self.right_flags -= 1
                return 'add' # Якщо флаг видалено
        else:
            return 'Err'

    def losing(self): # Ф-я поразки
        self.game_over = True
        self.background = shapes.Rectangle(0, H, W, 50, color=(200, 100, 100), batch = self.over_batch) # Фон
        self.lose_text = pyglet.text.Label( # Текст кнопки
                            'You are lose!(retry)',
                            font_name = 'Comic Sans MC',
                            font_size = W / 35,
                            x = W / 2, y = H + 25,
                            anchor_x = 'center', anchor_y = 'center')
        self.retry_butt = Button(W / 3.5, H + 10, W / 2.5, 30, (200, 100, 125), self.lose_text, batch = self.over_batch) # Кнопка

        for row in self.field:
            for obj in row:
                if obj.hide:
                    obj.disclosure()

    def winning(self): # Ф-я перемоги
        self.game_over = True
        self.background = shapes.Rectangle(0, H, W, 50, color=(100, 200, 100), batch = self.over_batch) # Фон
        self.win_text = pyglet.text.Label( # Текст кнопки
                            'You are win!(retry)',
                            font_name = 'Comic Sans MC',
                            font_size = W / 35,
                            x = W / 2, y = H + 25,
                            anchor_x = 'center', anchor_y = 'center')
        self.retry_butt = Button(W / 3.5, H + 10, W / 2.5, 30, (100, 200, 125), self.win_text, batch = self.over_batch) # Кнопка

    def draw(self): # Відмальовування порожніх клітинок, мін та прапорців
        for ec in self.empty_cells:
            ec.draw()
        for row in self.field:
            for obj in row:
                if obj.hide == False:
                    if type(obj).__name__ == 'Number' and obj.text == '0': # Не малюємо текст з надписом '0'
                        continue
                    obj.draw()
        for row in self.flags_matrix:
            for obj in row:
                if obj != 0:
                    obj.draw()



class UI: # Клас нашего інтерфейса
    def __init__(self):
        self.UI_batch = pyglet.graphics.Batch()
        self.net = []
        self.score = 0
        self.menu_batch = pyglet.graphics.Batch()

    def create_game_net(self): # Метод створення сітки ігрового поля
        for x in range(1, MAP_SIZE[0]):
            line_x = shapes.Rectangle(x * SIZE, 0, 1, H, color = (50, 50, 50), batch = self.UI_batch)
            self.net.append(line_x)
        for y in range(1, MAP_SIZE[1]):
            line_y = shapes.Rectangle(0, y * SIZE, W, 1, color = (50, 50, 50), batch = self.UI_batch)
            self.net.append(line_y)

    def create_score_text(self): # Метод створення тексту з балами
        self.score_text = pyglet.text.Label(
                            str(self.score),
                            font_name = 'Comic Sans MC',
                            font_size = SIZE / 1.5,
                            x = 25, y = H + 25,
                            anchor_x = 'center', anchor_y = 'center',
                            batch = self.UI_batch)
    def change_score(self, new): # Ф-я зміни тексту балів
        self.score = new
        self.score_text.text = str(new)

    def menu(self): # Доігрове меню
        self.background = shapes.Rectangle(0, 0, W, H + 50, color = (100, 100, 200), batch = self.menu_batch)
        #V Ползунок для вибору складності V#
        self.scroller = Scroller(W / 12, H / 2, 0, 40, 5, 40, batch = self.menu_batch)
        #V Кнопка та її текст V#
        label = pyglet.text.Label(
                            'Accept',
                            font_name = 'Comic Sans MC',
                            font_size = SIZE / 1.5,
                            x = 0, y = 0,
                            anchor_x = 'center', anchor_y = 'center')
        self.butt = Button(W / 3, H / 3, W / 3, H / 12, (100, 150, 100), label, batch = self.menu_batch)
        self.text = pyglet.text.Label(
                            'Choose difficulty',
                            font_name = 'Comic Sans MC',
                            font_size = 25,
                            x = W / 2, y = 0.9 * H,
                            anchor_x = 'center', anchor_y = 'center')

    def __add__(self, other): # Метод який дозволяє нам використовувати "+" для класа
        return self.score + int(other)

    def __sub__(self, other): # Метод який дозволяє нам використовувати "-" для класа
        return self.score - int(other)

    def draw(self): # Метод малювання інтерфейсу
        self.UI_batch.draw()
