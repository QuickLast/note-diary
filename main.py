from tkinter import ttk
from tkinter import *
import sqlite3

class Dictionary:
    db_name = 'dictionary_my.db'

    def __init__(self, window):

        self.wind = window
        self.wind.title('Редактирование дневника')

        # создание элементов для ввода слов и значений
        frame = LabelFrame(self.wind, text = 'Введите название для заметки')
        frame.grid(row = 0, column = 0, columnspan = 3, pady = 20)
        Label(frame, text = 'Название: ').grid(row = 1, column = 0)
        self.note = Entry(frame)
        self.note.focus()
        self.note.grid(row = 1, column = 1)
        Label(frame, text = 'Текст: ').grid(row = 2, column = 0)
        self.note_text = Entry(frame)
        self.note_text.grid(row = 2, column = 1)
        ttk.Button(frame, text = 'Сохранить', command = self.add_note).grid(row = 3, columnspan = 2, sticky = W + E)
        self.message = Label(text = '', fg = 'green')
        self.message.grid(row = 3, column = 0, columnspan = 2, sticky = W + E)
        # таблица слов и значений
        self.tree = ttk.Treeview(height = 10, columns = 2)
        self.tree.grid(row = 4, column = 0, columnspan = 2)
        self.tree.heading('#0', text = 'Заметка', anchor = CENTER)
        self.tree.heading('#1', text = 'Текст', anchor = CENTER)
        # кнопки редактирования записей
        ttk.Button(text = 'Удалить', command = self.delete_note).grid(row = 5, column = 0, sticky = W + E)
        ttk.Button(text = 'Изменить', command = self.edit_note).grid(row = 5, column = 1, sticky = W + E)

        # заполнение таблицы
        self.get_notes()

    # подключение и запрос к базе
    def run_query(self, query, parameters = ()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result

    # заполнение таблицы словами и их значениями
    def get_notes(self):
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        query = 'SELECT * FROM dictionary ORDER BY note_name DESC'
        db_rows = self.run_query(query)
        for row in db_rows:
            v = []
            v.append(row[2])
            self.tree.insert('', 1, text = row[1], values = v)
    # валидация ввода
    def validation(self):
        return len(self.note.get()) != 0 and len(self.note_text.get()) != 0
    # добавление нового слова
    def add_note(self):
        if self.validation():
            query = 'INSERT INTO dictionary VALUES(NULL, ?, ?)'
            parameters =  (self.note.get(), self.note_text.get())
            self.run_query(query, parameters)
            self.message['text'] = 'Заметка "{}" добавлена в дневник'.format(self.note.get())
            self.note.delete(0, END)
            self.note_text.delete(0, END)
        else:
            self.message['text'] = 'Введите название и текст заметки'
        self.get_notes()
    # удаление слова 
    def delete_note(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['text'][0]
        except IndexError as e:
            self.message['text'] = 'Выберите заметку, которую нужно удалить'
            return
        self.message['text'] = ''
        note = self.tree.item(self.tree.selection())['text']
        query = 'DELETE FROM dictionary WHERE note_name = ?'
        self.run_query(query, (note, ))
        self.message['text'] = 'Заметка "{}" успешно удалена'.format(note)
        self.get_notes()
    # рeдактирование слова и/или значения
    def edit_note(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['values']
        except IndexError as e:
            self.message['text'] = 'Выберите заметку для изменения'
            return
        note = self.tree.item(self.tree.selection())['text']
        old_note_text = self.tree.item(self.tree.selection())['values']
        self.edit_wind = Toplevel()
        self.edit_wind.title = 'Изменить заметку'

        Label(self.edit_wind, text = 'Прежнее имя заметки:').grid(row = 0, column = 1)
        Entry(self.edit_wind, textvariable = StringVar(self.edit_wind, value = note), state = 'readonly').grid(row = 0, column = 2)
        
        Label(self.edit_wind, text = 'Новое имя:').grid(row = 1, column = 1)
        # предзаполнение поля
        new_note = Entry(self.edit_wind, textvariable = StringVar(self.edit_wind, value = note))
        new_note.grid(row = 1, column = 2)


        Label(self.edit_wind, text = 'Прежний текст заметки:').grid(row = 2, column = 1)
        Entry(self.edit_wind, textvariable = StringVar(self.edit_wind, value = old_note_text), state = 'readonly').grid(row = 2, column = 2)
 
        Label(self.edit_wind, text = 'Новый текст заметки:').grid(row = 3, column = 1)
        # предзаполнение поля
        new_note_text= Entry(self.edit_wind, textvariable = StringVar(self.edit_wind, value = old_note_text))
        new_note_text.grid(row = 3, column = 2)

        Button(self.edit_wind, text = 'Изменить', command = lambda: self.edit_records(new_note.get(), note, new_note_text.get(), old_note_text)).grid(row = 4, column = 2, sticky = W)
        self.edit_wind.mainloop()
    # внесение изменений в базу
    def edit_records(self, new_note, note, new_note_text, old_note_text):
        query = 'UPDATE dictionary SET note_name = ?, note_text = ? WHERE note_name = ? AND note_text = ?'
        parameters = (new_note, new_note_text, note, old_note_text)
        self.run_query(query, parameters)
        self.edit_wind.destroy()
        self.message['text'] = 'Заметка {} успешно изменена'.format(note)
        self.get_notes()

if __name__ == '__main__':
    window = Tk()
    application = Dictionary(window)
    window.mainloop()
