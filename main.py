import csv
import random
import chardet
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition


def positive_name():
    lista = []
    with open('positive.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            lista.append(row[0])
    return random.choice(lista)


def new_index():
    data = App.get_running_app().data
    if not data:
        return None  # bezpieczeństwo dla pustej listy

    max_val = int(data[0]["INDEX"])
    for line in data:
        if int(line["INDEX"]) > max_val:
            max_val = int(line["INDEX"])
    return max_val+1


def show_confirm_popup(instance):
    content = BoxLayout(orientation='vertical', spacing=10, padding=10)
    label = Label(text="Do you really want to exit?", halign="center")

    # buttons
    buttons = BoxLayout(orientation='horizontal', spacing=10)
    yes_btn = Button(text="Yes", size_hint=(0.5, 1))
    no_btn = Button(text="No", size_hint=(0.5, 1))

    buttons.add_widget(yes_btn)
    buttons.add_widget(no_btn)
    content.add_widget(label)
    content.add_widget(buttons)

    # popup
    popup = Popup(
        title="Confirm",
        content=content,
        size_hint=(0.6, 0.4),
        auto_dismiss=False  # do not close after click
    )

    # action
    yes_btn.bind(on_press=lambda x: App.get_running_app().stop())  # close app
    no_btn.bind(on_press=lambda x: popup.dismiss())  # close popup

    popup.open()


class AppButtons:
    @staticmethod
    def settings_button():
        button = Button(
            background_normal='graphics/settings.png',  # obrazek jako tło
            background_down='graphics/settings_on_press.png',  # opcjonalnie inny obraz po kliknięciu
            size_hint=(None, None)
        )
        return button

    @staticmethod
    def exit_button():
        button = Button(
            background_normal='graphics/exit.png',  # obrazek jako tło
            background_down='graphics/exit_on_press.png',  # opcjonalnie inny obraz po kliknięciu
            size_hint=(None, None)
        )
        return button

    @staticmethod
    def remove_button():
        button = Button(
            background_normal='graphics/remove.png',  # obrazek jako tło
            background_down='graphics/remove_on_press.png',  # opcjonalnie inny obraz po kliknięciu
            size_hint=(None, None)
        )
        return button

    @staticmethod
    def dictionary_button():
        button = Button(
            background_normal='graphics/dictionary.png',  # obrazek jako tło
            background_down='graphics/dictionary_on_press.png',  # opcjonalnie inny obraz po kliknięciu
            size_hint=(None, None)
        )
        return button

    @staticmethod
    def menu_button():
        button = Button(
            background_normal='graphics/menu.png',  # obrazek jako tło
            background_down='graphics/menu_on_press.png',  # opcjonalnie inny obraz po kliknięciu
            size_hint=(None, None)
        )
        return button


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Ustawienie rozmiaru okna (np. smartfon 9:16, np. 360x640)
        Window.size = (360, 640)

        with self.canvas.before:
            Color(0.404, 0.698, 0.906, 1)  # RGB + Alpha (czyli przezroczystość)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        # aktualizuj prostokąt przy zmianie rozmiaru lub pozycji
        self.bind(size=update_rect, pos=update_rect)

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Logo
        logo_label = Image(source="graphics/logo.jpeg", size_hint_y=1.2)
        layout.add_widget(logo_label)

        # przyciski w poziomie
        buttons = BoxLayout(orientation='vertical', spacing=10)
        noun_button = Button(text="Noun", size_hint=(1, 0.2))
        noun_button.bind(on_press=lambda x: goto_noun(self, x))
        verb_button = Button(text="Verb", size_hint=(1, 0.2))
        noun_button.bind(on_press=lambda x: goto_verb(self, x))

        buttons.add_widget(noun_button)
        buttons.add_widget(verb_button)

        layout.add_widget(buttons)

        settings_button = AppButtons.settings_button()
        settings_button.bind(on_press=lambda x: goto_settings(self, x))
        exit_button = AppButtons.exit_button()
        exit_button.bind(on_press=show_confirm_popup)
        dictionary_button = AppButtons.dictionary_button()
        dictionary_button.bind(on_press=lambda x: goto_dictionary(self, x))
        menu_button = AppButtons.menu_button()
        menu_button.bind(on_press=lambda x: goto_menu(self, x))

        menu_anchor = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1, None), height=120)

        menu = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        menu.add_widget(Widget(size_hint=(1, 1)))
        menu.add_widget(menu_button)
        menu.add_widget(dictionary_button)
        menu.add_widget(settings_button)
        menu.add_widget(exit_button)
        menu.add_widget(Widget(size_hint=(1, 1)))
        menu_anchor.add_widget(menu)

        layout.add_widget(menu_anchor)
        self.add_widget(layout)


class NounScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Wczytanie danych z pliku

        self.data = App.get_running_app().data
        self.selected = ""
        # Aktualne słowo
        self.current_word = None
        self.waiting_for_answer = True  # flaga: czekamy na odpowiedź użytkownika

        # Ustawienie rozmiaru okna (np. smartfon 9:16, np. 360x640)
        Window.size = (360, 640)

        with self.canvas.before:
            Color(0.404, 0.698, 0.906, 1)  # RGB + Alpha (czyli przezroczystość)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        # aktualizuj prostokąt przy zmianie rozmiaru lub pozycji
        self.bind(size=update_rect, pos=update_rect)

        layout = BoxLayout(orientation="vertical", padding=10, spacing=5)

        # Etykieta z polskim słowem
        self.word_label = Label(text="Place for word", markup=True, halign="center", valign="middle",
                                size_hint_y=0.4)
        layout.add_widget(self.word_label)

        article_box = BoxLayout(orientation="horizontal", padding=10, spacing=5)
        # Przyciski der, die, das
        self.button_der = Button(text="der", size_hint_y=0.15, background_color=(0, 0, 1, 1))
        self.button_der.bind(on_press=self.on_button_der)
        article_box.add_widget(self.button_der)
        self.button_die = Button(text="die", size_hint_y=0.15, background_color=(0, 0, 1, 1))
        self.button_die.bind(on_press=self.on_button_die)
        article_box.add_widget(self.button_die)
        self.button_das = Button(text="das", size_hint_y=0.15, background_color=(0, 0, 1, 1))
        self.button_das.bind(on_press=self.on_button_das)
        article_box.add_widget(self.button_das)
        layout.add_widget(article_box)


        # Pole 1
        self.input1 = TextInput(hint_text="Type translation", halign="center", multiline=False, size_hint_y=0.2)
        layout.add_widget(self.input1)
        # Wynik
        self.result = Label(text="Tutaj będę Cię obrażał", size_hint_y=0.2)
        layout.add_widget(self.result)


        # Confirm button
        self.button = Button(text="Check", size_hint_y=0.2)
        self.button.bind(on_press=self.on_button_press)
        layout.add_widget(self.button)



        # Remove button
        self.button_remove = Button(text="Remove word", size_hint_y=0.2)
        self.button_remove.bind(on_press=lambda instance: remove_word(App.get_running_app().noun_index, self))
        layout.add_widget(self.button_remove)



        # menu
        settings_button = AppButtons.settings_button()
        settings_button.bind(on_press=lambda x: goto_settings(self, x))
        exit_button = AppButtons.exit_button()
        exit_button.bind(on_press=show_confirm_popup)
        dictionary_button = AppButtons.dictionary_button()
        dictionary_button.bind(on_press=lambda x: goto_dictionary(self, x))
        menu_button = AppButtons.menu_button()
        menu_button.bind(on_press=lambda x: goto_menu(self, x))

        menu_anchor = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1, None), height=120)

        menu = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        menu.add_widget(Widget(size_hint=(1, 1)))
        menu.add_widget(menu_button)
        menu.add_widget(dictionary_button)
        menu.add_widget(settings_button)
        menu.add_widget(exit_button)
        menu.add_widget(Widget(size_hint=(1, 1)))
        menu_anchor.add_widget(menu)

        layout.add_widget(menu_anchor)
        self.add_widget(layout)
        # Wylosuj pierwsze słowo
        self.next_word()

    def on_button_press(self, instance):

        if self.waiting_for_answer:
            if not self.current_word:
                self.next_word()
                print("test1")
                return
            answer1 = self.input1.text.strip()
            correct1 = self.current_word["SINGULAR"]

            answer2 = self.selected
            correct2 = self.current_word["ARTIKEL"]
            print(f"Rodzajnik wybrany to'{answer2}', a powinno być '{correct2}'")

            if answer1.lower() == correct1.lower() and answer2 == correct2:
                self.result.text = f"Brawo {positive_name()}! Dobrze!"
                self.current_word['POINTS_WORD'] = int(self.current_word.get('POINTS_WORD', 0)) + 1
            else:
                self.result.text = f"Źle! Poprawna odpowiedź: {correct2} {correct1}"

            self.button.text = "Następne słowo"
            self.selected = ""
            self.waiting_for_answer = False

        # jeśli już pokazano wynik -> losujemy nowe słowo
        else:
            self.next_word()

    def on_button_der(self, instance):
        self.selected = "der"
        self.button_der.background_color = (0, 1, 0, 1)
        self.button_die.background_color = (0, 0, 1, 1)
        self.button_das.background_color = (0, 0, 1, 1)

    def on_button_die(self, instance):
        self.selected = "die"
        self.button_der.background_color = (0, 0, 1, 1)
        self.button_die.background_color = (0, 1, 0, 1)
        self.button_das.background_color = (0, 0, 1, 1)

    def on_button_das(self, instance):
        self.selected = "das"
        self.button_der.background_color = (0, 0, 1, 1)
        self.button_die.background_color = (0, 0, 1, 1)
        self.button_das.background_color = (0, 1, 0, 1)

    def next_word(self):

        # nowe slowo
        n = App.get_running_app().limit_number

        for wiersz in self.data:
            if wiersz['POINTS_WORD'] < n:
                n = wiersz['POINTS_WORD']
        print(f"liczba n={n}")
        new_data = [x for x in self.data if x['POINTS_WORD'] == n]

        self.current_word = random.choice(new_data)
        print(self.current_word)
        App.get_running_app().noun_index = int(self.current_word["INDEX"])
        print(App.get_running_app().noun_index)

        self.word_label.text = f"Tłumacz na niemiecki:\n [size=50]{self.current_word['PL']}[/size]"
        self.result.text = ""
        self.input1.text = ""
        self.button.text = "Sprawdź"
        self.waiting_for_answer = True
        self.selected = ""
        self.button_der.background_color = (0, 0, 1, 1)
        self.button_die.background_color = (0, 0, 1, 1)
        self.button_das.background_color = (0, 0, 1, 1)


class VerbScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Ustawienie rozmiaru okna (np. smartfon 9:16, np. 360x640)
        Window.size = (360, 640)

        with self.canvas.before:
            Color(0.404, 0.698, 0.906, 1)  # RGB + Alpha (czyli przezroczystość)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        # aktualizuj prostokąt przy zmianie rozmiaru lub pozycji
        self.bind(size=update_rect, pos=update_rect)

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Logo
        logo_label = Image(source="graphics/logo.jpeg", size_hint_y=1.2)
        layout.add_widget(logo_label)

        # przyciski w poziomie
        buttons = BoxLayout(orientation='vertical', spacing=10)
        noun_write_button = Button(text="Noun", size_hint=(1, 0.2))
        verb_write_button = Button(text="Verb", size_hint=(1, 0.2))

        buttons.add_widget(noun_write_button)
        buttons.add_widget(verb_write_button)

        layout.add_widget(buttons)

        settings_button = AppButtons.settings_button()
        settings_button.bind(on_press=lambda x: goto_settings(self, x))
        remove_button = AppButtons.remove_button()
        remove_button.bind(on_press=show_confirm_popup)
        exit_button = AppButtons.exit_button()
        exit_button.bind(on_press=show_confirm_popup)
        dictionary_button = AppButtons.dictionary_button()
        dictionary_button.bind(on_press=lambda x: goto_dictionary(self, x))
        menu_button = AppButtons.menu_button()
        menu_button.bind(on_press=lambda x: goto_menu(self, x))

        menu = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        menu.add_widget(Widget(size_hint=(1, 1)))

        menu.add_widget(menu_button)

        menu.add_widget(dictionary_button)
        menu.add_widget(settings_button)
        # menu.add_widget(exit_button)
        menu.add_widget(remove_button)
        menu.add_widget(Widget(size_hint=(1, 1)))
        layout.add_widget(menu)
        footer = Label(
            text="© 2025 Pan Kamil",
            size_hint_y=0.2,
            halign="center",
            valign="middle"
        )
        footer.bind(size=lambda *x: setattr(footer, 'text_size', footer.size))
        layout.add_widget(footer)

        self.add_widget(layout)


class DictionaryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Ustawienie rozmiaru okna (np. smartfon 9:16, np. 360x640)
        Window.size = (360, 640)

        with self.canvas.before:
            Color(0.404, 0.698, 0.906, 1)  # RGB + Alpha (czyli przezroczystość)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        # aktualizuj prostokąt przy zmianie rozmiaru lub pozycji
        self.bind(size=update_rect, pos=update_rect)

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        scroll = ScrollView(size_hint=(1, 1), bar_width=20)

        self.inner_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        self.inner_layout.bind(minimum_height=lambda inst, val: setattr(inst, 'height', val))

        self.n_list = 0

        for i, line in enumerate(App.get_running_app().data[self.n_list * 100:self.n_list * 100 + 100]):
            inner_line = BoxLayout(orientation='horizontal', size_hint_y=None)
            button = Button(text=f"remove {line['INDEX']}", size_hint_x=0.3)
            button.bind(on_press=lambda instance, idx=line['INDEX']: (remove_word(int(idx), self), self.refresh_list()))
            label = Label(
                text=f"{i + self.n_list * 100}: [b]{line['PL']}[/b]\n {line['ARTIKEL']} | {line['SINGULAR']}\nPunkty: {line['POINTS_WORD']} ",
                markup=True,
                size_hint_y=None,
                height=70,
                halign="left",
                valign="middle",
            )
            label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
            inner_line.add_widget(button)
            inner_line.height = label.height
            inner_line.add_widget(label)
            self.inner_layout.add_widget(inner_line)
        scroll.add_widget(self.inner_layout)
        layout.add_widget(scroll)

        layout.add_widget(Widget(size_hint_y=0.1))

        limit_box = BoxLayout(orientation='horizontal', spacing=10, padding=10, size_hint=(1, 1))

        # przycisk w dół
        btn_down = Button(background_normal='graphics/left.png', size_hint=(2, 2))
        btn_down.bind(on_press=self.decrease)
        limit_box.add_widget(btn_down)

        # etykieta z wartością
        self.page_label = Label(text=str(f"{self.n_list * 100} - {self.n_list * 100 + 99}"), font_size=32,
                                size_hint=(2, 2))
        limit_box.add_widget(self.page_label)

        # przycisk w górę
        btn_up = Button(background_normal='graphics/right.png', size_hint=(2, 2))
        btn_up.bind(on_press=self.increase)
        limit_box.add_widget(btn_up)

        limit_anchor = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1, 0.1))
        limit_anchor.add_widget(limit_box)
        layout.add_widget(limit_anchor)

        # New word button
        self.new_word_button = Button(text="New word", size_hint_y=0.2)
        self.new_word_button.bind(on_press=self.new_word_popup)
        layout.add_widget(self.new_word_button)
        # menu
        settings_button = AppButtons.settings_button()
        settings_button.bind(on_press=lambda x: goto_settings(self, x))
        exit_button = AppButtons.exit_button()
        exit_button.bind(on_press=show_confirm_popup)
        dictionary_button = AppButtons.dictionary_button()
        dictionary_button.bind(on_press=lambda x: goto_dictionary(self, x))
        menu_button = AppButtons.menu_button()
        menu_button.bind(on_press=lambda x: goto_menu(self, x))

        menu_anchor = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1, None), height=120)

        menu = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        menu.add_widget(Widget(size_hint=(1, 1)))
        menu.add_widget(menu_button)
        menu.add_widget(dictionary_button)
        menu.add_widget(settings_button)
        menu.add_widget(exit_button)
        menu.add_widget(Widget(size_hint=(1, 1)))
        menu_anchor.add_widget(menu)

        layout.add_widget(menu_anchor)
        self.add_widget(layout)

    def increase(self, instance):
        self.n_list += 1
        self.page_label.text = f"{self.n_list * 100} - {self.n_list * 100 + 99}"
        print(self.n_list)
        self.refresh_list()

    def decrease(self, instance):
        if self.n_list > 0:
            self.n_list -= 1
        self.page_label.text = f"{self.n_list * 100} - {self.n_list * 100 + 99}"
        print(self.n_list)
        self.refresh_list()

    def refresh_list(self):
        app = App.get_running_app()

        # wyczyść zawartość listy
        self.inner_layout.clear_widgets()

        # wygeneruj ponownie 100 pozycji
        start = self.n_list * 100
        end = start + 100

        for i, line in enumerate(app.data[start:end]):
            inner_line = BoxLayout(orientation='horizontal', size_hint_y=None)
            button = Button(text=f"remove {line['INDEX']}", size_hint_x=0.3)
            button.bind(on_press=lambda instance, idx=line['INDEX']: (remove_word(int(idx), self), self.refresh_list()))

            label = Label(
                text=f"{i + start}: [b]{line['PL']}[/b]\n {line['ARTIKEL']} | {line['SINGULAR']}\nPunkty: {line['POINTS_WORD']}",
                markup=True,
                size_hint_y=None,
                height=70,
                halign="left",
                valign="middle",
            )
            label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

            inner_line.add_widget(button)
            inner_line.add_widget(label)
            inner_line.height = label.height

            self.inner_layout.add_widget(inner_line)

    def new_word_popup(self, instance):
        # zawartość okienka
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # index
        line0=BoxLayout(orientation='horizontal', size_hint_y=0.3)
        label_0 = Label(text="index", markup=True, halign="center", valign="middle")
        label_01 = Label(text=f"{new_index()}", markup=True, halign="center", valign="middle")
        line0.add_widget(label_0)
        line0.add_widget(label_01)
        content.add_widget(line0)

        # polish
        line1=BoxLayout(orientation='horizontal', size_hint_y=0.3)
        label_1 = Label(text="polish", markup=True, halign="center", valign="middle")
        self.input_1 = TextInput(hint_text="", halign="center", multiline=False)
        line1.add_widget(label_1)
        line1.add_widget(self.input_1)
        content.add_widget(line1)

        # article
        line2=BoxLayout(orientation='horizontal', size_hint_y=0.3)
        label_2 = Label(text="article", markup=True, halign="center", valign="middle")
        self.input_2 = TextInput(hint_text="", halign="center", multiline=False)
        line2.add_widget(label_2)
        line2.add_widget(self.input_2)
        content.add_widget(line2)

        #german - singular
        line3=BoxLayout(orientation='horizontal', size_hint_y=0.3)
        label_3 = Label(text="singular", markup=True, halign="center", valign="middle")
        self.input_3 = TextInput(hint_text="", halign="center", multiline=False)
        line3.add_widget(label_3)
        line3.add_widget(self.input_3)
        content.add_widget(line3)

        # german - plural
        line4 = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        label_4 = Label(text="plural", markup=True, halign="center", valign="middle")
        self.input_4 = TextInput(hint_text="", halign="center", multiline=False)
        line4.add_widget(label_4)
        line4.add_widget(self.input_4)
        content.add_widget(line4)

        close_btn = Button(text="add new word", size_hint=(1, 0.1))
        content.add_widget(close_btn)

        close_btn.bind(on_press=self.add_new_word)
        self.popup = Popup(
            title="add new word",
            content=content,
            size_hint=(1, 1),
            auto_dismiss=False  # nie zamykaj po kliknięciu w tło
        )

        self.popup.open()

    def add_new_word(self, instance):
        word = {"INDEX":new_index(),
                "PL":self.input_1.text.strip(),
                "ARTIKEL":self.input_2.text.strip(),
                "SINGULAR":self.input_3.text.strip(),
                "PLURAL":self.input_4.text.strip(),
                "POINTS_WORD": 0
                }
        App.get_running_app().data.append(word)
        self.popup.dismiss()


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Ustawienie rozmiaru okna (np. smartfon 9:16, np. 360x640)
        Window.size = (360, 640)

        with self.canvas.before:
            Color(0.404, 0.698, 0.906, 1)  # RGB + Alpha (czyli przezroczystość)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        # aktualizuj prostokąt przy zmianie rozmiaru lub pozycji
        self.bind(size=update_rect, pos=update_rect)

        # zawartość okienka
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        limit_label = Label(text="Limit number for words:", halign="center")
        layout.add_widget(limit_label)
        limit_anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.3))
        limit_box = BoxLayout(orientation='horizontal', spacing=10, padding=10, size_hint=(0.6, 0.5))

        def increase(instance):
            App.get_running_app().limit_number += 1
            label.text = str(App.get_running_app().limit_number)

        def decrease(instance):
            App.get_running_app().limit_number -= 1
            label.text = str(App.get_running_app().limit_number)

        # przycisk w dół
        btn_down = Button(background_normal='graphics/left.png', size_hint=(2, 2))
        btn_down.bind(on_press=decrease)
        limit_box.add_widget(btn_down)

        # etykieta z wartością
        label = Label(text=str("ppp"), font_size=32, size_hint=(2, 2))
        limit_box.add_widget(label)

        # przycisk w górę
        btn_up = Button(background_normal='graphics/right.png', size_hint=(2, 2))
        btn_up.bind(on_press=increase)
        limit_box.add_widget(btn_up)

        limit_anchor.add_widget(limit_box)
        layout.add_widget(limit_anchor)

        # przyciski w poziomie
        btns = BoxLayout(orientation='horizontal', spacing=10)
        yes_btn = Button(text="Tak", size_hint=(0.5, 1))
        no_btn = Button(text="Nie", size_hint=(0.5, 1))

        btns.add_widget(yes_btn)
        btns.add_widget(no_btn)

        layout.add_widget(btns)

        settings_button = AppButtons.settings_button()
        settings_button.bind(on_press=lambda x: goto_settings(self, x))
        exit_button = AppButtons.exit_button()
        exit_button.bind(on_press=show_confirm_popup)
        dictionary_button = AppButtons.dictionary_button()
        dictionary_button.bind(on_press=lambda x: goto_dictionary(self, x))
        menu_button = AppButtons.menu_button()
        menu_button.bind(on_press=lambda x: goto_menu(self, x))

        menu_anchor = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1, None), height=120)

        menu = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        menu.add_widget(Widget(size_hint=(1, 1)))
        menu.add_widget(menu_button)
        menu.add_widget(dictionary_button)
        menu.add_widget(settings_button)
        menu.add_widget(exit_button)
        menu.add_widget(Widget(size_hint=(1, 1)))
        menu_anchor.add_widget(menu)

        layout.add_widget(menu_anchor)
        self.add_widget(layout)


def remove_word(index, instance):
    print(f"Usunięto słowo o indexie{index}")
    for i, item in enumerate(App.get_running_app().data):
        print(f" itemget {item.get('INDEX')} index{index}")
        if int(item.get("INDEX")) == index:
            print("Usuwanko")
            del App.get_running_app().data[i]
            break


def _resize_logo(instance, value):
    instance.text_size = instance.size
    instance.font_size = instance.height * 0.9


def goto_settings(screen, instance):
    screen.manager.current = "settings"


def goto_menu(screen, instance):
    screen.manager.current = "main"


def goto_noun(screen, instance):
    screen.manager.current = "noun"


def goto_verb(screen, instance):
    screen.manager.current = "verb"


def goto_dictionary(screen, instance):
    screen.manager.current = "dictionary"


def update_rect(self, *args):
    self.rect.pos = self.pos
    self.rect.size = self.size


def on_select(self, checkbox, value):
    if value:
        self.selected = self.options[checkbox]


def open_data():
    plik_csv = "data.csv"  # <-- tutaj podaj nazwę swojego pliku
    nazwy_kolumn = ["INDEX", "PL", "ARTIKEL", "SINGULAR", "PLURAL", "POINTS_WORD", "POINTS_ARTICLE"]

    # --- KROK 1: automatyczne wykrycie kodowania ---
    with open(plik_csv, 'rb') as f:
        wynik = chardet.detect(f.read(5000))
        kodowanie = wynik['encoding']

    # Wczytanie zawartości pliku
    with open(plik_csv, newline='', encoding=kodowanie) as f:
        reader = csv.DictReader(f, fieldnames=nazwy_kolumn, delimiter=';')
        data = list(reader)

    for wiersz in data:
        try:
            wiersz['POINTS_WORD'] = int(wiersz['POINTS_WORD'])
        except (ValueError, TypeError):
            wiersz['POINTS_WORD'] = 0

    return data


def save_data(_data):
    plik_csv = "data.csv"  # <-- tutaj podaj nazwę swojego pliku

    nazwy_kolumn = ["INDEX", "PL", "ARTIKEL", "SINGULAR", "PLURAL", "POINTS_WORD", "POINTS_ARTICLE"]
    # --- KROK 1: automatyczne wykrycie kodowania ---
    with open(plik_csv, 'rb') as f:
        wynik = chardet.detect(f.read(5000))
        kodowanie = wynik['encoding']

    with open("data.csv", mode="w", newline='', encoding=kodowanie) as f:
        writer = csv.DictWriter(f, fieldnames=nazwy_kolumn, delimiter=';')

        # Zapisujemy wiersze (słowniki)
        for wiersz in _data:
            writer.writerow(wiersz)


def on_button_exit(instance):
    App.get_running_app().stop()





class FischkiApp(App):
    limit_number = 10
    verb_index = 0
    noun_index = 0
    # list of dicts
    data = open_data()

    answer_noun = "answer1"
    correct_noun = "correct1"

    answer_article = "answer2"
    correct_article = "correct2"

    def build(self):
        sm = ScreenManager(transition=FadeTransition())

        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(NounScreen(name="noun"))
        sm.add_widget(VerbScreen(name="verb"))
        sm.add_widget(DictionaryScreen(name="dictionary"))

        return sm

    def on_stop(self):
        """Zapisz dane po zamknięciu aplikacji"""
        save_data(self.data)
        print("✅ Dane zapisane do pliku data.csv przed zamknięciem.")


if __name__ == "__main__":
    FischkiApp().run()
