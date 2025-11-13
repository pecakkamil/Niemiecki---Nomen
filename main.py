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


def positive_name():
    lista = []
    with open('positive.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            lista.append(row[0])
    return random.choice(lista)


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


class Nomen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)

        # Wczytanie danych z pliku
        self.limit_number = 10
        self.data = self.open_data()

        # Aktualne słowo
        self.current_word = None
        self.waiting_for_answer = True  # flaga: czekamy na odpowiedź użytkownika

        self.build_ui()

        # Wylosuj pierwsze słowo
        self.next_word()

    @staticmethod
    def _resize_logo(instance, value):
        instance.text_size = instance.size
        instance.font_size = instance.height * 0.9

    def build_ui(self):

        # Ustawienie rozmiaru okna (np. smartfon 9:16, np. 360x640)
        Window.size = (360, 640)

        with self.canvas.before:
            Color(0.404, 0.698, 0.906, 1)  # RGB + Alpha (czyli przezroczystość)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        # aktualizuj prostokąt przy zmianie rozmiaru lub pozycji
        self.bind(size=self.update_rect, pos=self.update_rect)

        def update_text_size(instance, value):
            # instance.text_size = instance.size
            # font_size proporcjonalny do wysokości okna
            instance.font_size = instance.height * value  # 40% wysokości boxa = rozmiar czcionki

        # Logo
        self.logo_label = Image(source="graphics/logo.jpeg", size_hint_y=1.2)
        self.add_widget(self.logo_label)

        self.exit_button = Button(
            background_normal='graphics/exit.png',  # obrazek jako tło
            background_down='graphics/menu_on_press.png',  # opcjonalnie inny obraz po kliknięciu
            size_hint=(None, None)
        )
        self.exit_button.bind(on_press=self.on_button_exit)
        self.menu_button = Button(
            background_normal='graphics/menu.png',  # obrazek jako tło
            background_down='graphics/settings_on_press.png',  # opcjonalnie inny obraz po kliknięciu
            size_hint=(None, None)
        )
        self.menu_button.bind(on_press=self.menu_popup)
        self.remove_button = Button(
            background_normal='graphics/remove.png',  # obrazek jako tło
            background_down='graphics/remove_on_press.png',  # opcjonalnie inny obraz po kliknięciu
            size_hint=(None, None)
        )
        self.remove_button.bind(on_press=show_confirm_popup)

        self.menu = BoxLayout(orientation='horizontal', size_hint=(1, 0.4))
        self.menu.add_widget(Widget(size_hint=(1, 1)))
        self.menu.add_widget(self.exit_button)
        self.menu.add_widget(Widget(size_hint=(1, 1)))
        self.menu.add_widget(self.menu_button)
        self.menu.add_widget(Widget(size_hint=(1, 1)))
        self.menu.add_widget(self.remove_button)
        self.menu.add_widget(Widget(size_hint=(1, 1)))
        self.add_widget(self.menu)

        # Etykieta z polskim słowem
        self.word_label = Label(text="Kliknij, aby wylosować słowo", markup=True, halign="center", valign="middle",
                                size_hint_y=0.4)
        self.add_widget(self.word_label)

        # Przyciski der, die, das
        self.button_der = Button(text="der", size_hint_y=0.2, background_color=(0, 0, 1, 1))
        self.button_der.bind(on_press=self.on_button_der)
        self.add_widget(self.button_der)
        self.button_die = Button(text="die", size_hint_y=0.2, background_color=(0, 0, 1, 1))
        self.button_die.bind(on_press=self.on_button_die)
        self.add_widget(self.button_die)
        self.button_das = Button(text="das", size_hint_y=0.2, background_color=(0, 0, 1, 1))
        self.button_das.bind(on_press=self.on_button_das)
        self.add_widget(self.button_das)

        # Pole 1
        self.input1 = TextInput(hint_text="Podaj tłumaczenie", halign="center", multiline=False, size_hint_y=0.4)
        update_text_size(self.input1, 0.5)
        self.add_widget(self.input1)

        # Przycisk
        self.button = Button(text="Sprawdź", size_hint_y=0.2)
        self.button.bind(on_press=self.on_button_press)
        self.add_widget(self.button)

        # Wynik
        self.result = Label(text="Tutaj będę Cię obrażał", size_hint_y=0.2)
        update_text_size(self.result, 0.5)
        self.add_widget(self.result)

        footer = Label(
            text="© 2025 Kamil P",
            size_hint_y=0.2,
            halign="center",
            valign="middle"
        )
        footer.bind(size=lambda *x: setattr(footer, 'text_size', footer.size))
        self.add_widget(footer)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_select(self, checkbox, value):
        if value:
            self.selected = self.options[checkbox]

    def open_data(self):
        plik_csv = "data.csv"  # <-- tutaj podaj nazwę swojego pliku
        nazwy_kolumn = ["PL", "ARTIKEL", "SINGULAR", "PLURAL", "POINTS_WORD", "POINTS_ARTICLE"]

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

    def save_data(self, _data):
        plik_csv = "data.csv"  # <-- tutaj podaj nazwę swojego pliku

        nazwy_kolumn = ["PL", "ARTIKEL", "SINGULAR", "PLURAL", "POINTS_WORD", "POINTS_ARTICLE"]
        # --- KROK 1: automatyczne wykrycie kodowania ---
        with open(plik_csv, 'rb') as f:
            wynik = chardet.detect(f.read(5000))
            kodowanie = wynik['encoding']

        with open("data.csv", mode="w", newline='', encoding=kodowanie) as f:
            writer = csv.DictWriter(f, fieldnames=nazwy_kolumn, delimiter=';')

            # Zapisujemy wiersze (słowniki)
            for wiersz in _data:
                writer.writerow(wiersz)

    def next_word(self):

        # nowe slowo
        n = self.limit_number

        for wiersz in self.data:
            if wiersz['POINTS_WORD'] < n:
                n = wiersz['POINTS_WORD']
        print(f"liczba n={n}")
        new_data = [x for x in self.data if x['POINTS_WORD'] == n]

        self.current_word = random.choice(new_data)

        self.word_label.text = f"Tłumacz na niemiecki:\n [size=50]{self.current_word['PL']}[/size]"
        self.result.text = ""
        self.input1.text = ""
        self.button.text = "Sprawdź"
        self.waiting_for_answer = True
        self.selected = ""
        self.button_der.background_color = (0, 0, 1, 1)
        self.button_die.background_color = (0, 0, 1, 1)
        self.button_das.background_color = (0, 0, 1, 1)

    def on_button_press(self, instance):
        if self.waiting_for_answer:
            if not self.current_word:
                self.next_word()
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

            # Wylosuj kolejne słowo po odpowiedzi
            # self.next_word()

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

    def on_button_exit(self, instance):
        App.get_running_app().stop()

    def menu_popup(self, instance):
        # zawartość okienka
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # popup
        popup = Popup(
            title="Menu",
            content=content,
            size_hint=(1, 1),
            auto_dismiss=False  # nie zamykaj po kliknięciu w tło
        )

        word_list_btn = Button(text="word list", size_hint=(1, 0.3))
        content.add_widget(word_list_btn)
        word_list_btn.bind(on_press=self.word_list_popup)

        settings_btn = Button(text="settings", size_hint=(1, 0.3))
        content.add_widget(settings_btn)
        settings_btn.bind(on_press=self.settings_popup)

        close_btn = Button(text="close menu", size_hint=(1, 0.3))
        content.add_widget(close_btn)
        close_btn.bind(on_press=lambda x: popup.dismiss())

        popup.open()

    def settings_popup(self, instance):
        # zawartość okienka
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        limit_label = Label(text="Limit number for words:", halign="center")
        content.add_widget(limit_label)
        limit_anchor=AnchorLayout(anchor_x='center', anchor_y='center',size_hint=(1, 0.3))
        limit_box = BoxLayout(orientation='horizontal', spacing=10, padding=10,size_hint=(0.6, 0.5))

        def increase(instance):
            self.limit_number += 1
            label.text = str(self.limit_number)

        def decrease(instance):
            self.limit_number -= 1
            label.text = str(self.limit_number)

        # przycisk w dół
        btn_down = Button(background_normal='graphics/left.png')
        btn_down.bind(on_press=decrease)
        limit_box.add_widget(btn_down)

        # etykieta z wartością
        label = Label(text=str(self.limit_number), font_size=32)
        limit_box.add_widget(label)

        # przycisk w górę
        btn_up = Button(background_normal='graphics/right.png')
        btn_up.bind(on_press=increase)
        limit_box.add_widget(btn_up)
        limit_anchor.add_widget(limit_box)
        content.add_widget(limit_anchor)

        # przyciski w poziomie
        btns = BoxLayout(orientation='horizontal', spacing=10)
        yes_btn = Button(text="Tak", size_hint=(0.5, 1))
        no_btn = Button(text="Nie", size_hint=(0.5, 1))

        btns.add_widget(yes_btn)
        btns.add_widget(no_btn)

        content.add_widget(btns)

        # popup
        popup = Popup(
            title="Settings",
            content=content,
            size_hint=(1, 1),
            auto_dismiss=False  # nie zamykaj po kliknięciu w tło
        )

        # akcje
        yes_btn.bind(on_press=lambda x: App.get_running_app().stop())  # zamknij aplikację
        no_btn.bind(on_press=lambda x: popup.dismiss())  # zamknij popup



        close_btn = Button(text="close setting", size_hint=(1, 0.3))
        content.add_widget(close_btn)
        close_btn.bind(on_press=lambda x: popup.dismiss())

        popup.open()

    def word_list_popup(self, instance):
        # zawartość okienka
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        scroll = ScrollView(size_hint=(1, 0.8), bar_width=20)

        inner_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        inner_layout.bind(minimum_height=lambda inst, val: setattr(inst, 'height', val))

        # ["PL", "ARTIKEL", "SINGULAR", "PLURAL", "POINTS_WORD", "POINTS_ARTICLE"]

        test_data = [
            {
                "PL": "ryba",
                "ARTIKEL": "der",
                "SINGULAR": "Fisch",
                "PLURAL": "Fische",
                "POINTS_WORD": 2,
                "POINTS_ARTICLE": 1
            },
            {
                "PL": "kot",
                "ARTIKEL": "die",
                "SINGULAR": "Katze",
                "PLURAL": "Katzen",
                "POINTS_WORD": 5,
                "POINTS_ARTICLE": 3
            },
            {
                "PL": "dziecko",
                "ARTIKEL": "das",
                "SINGULAR": "Kind",
                "PLURAL": "Kinder",
                "POINTS_WORD": 0,
                "POINTS_ARTICLE": 0
            },
            {
                "PL": "ryba",
                "ARTIKEL": "der",
                "SINGULAR": "Fisch",
                "PLURAL": "Fische",
                "POINTS_WORD": 2,
                "POINTS_ARTICLE": 1
            },
            {
                "PL": "kot",
                "ARTIKEL": "die",
                "SINGULAR": "Katze",
                "PLURAL": "Katzen",
                "POINTS_WORD": 5,
                "POINTS_ARTICLE": 3
            },
            {
                "PL": "dziecko",
                "ARTIKEL": "das",
                "SINGULAR": "Kind",
                "PLURAL": "Kinder",
                "POINTS_WORD": 0,
                "POINTS_ARTICLE": 0
            },
            {
                "PL": "ryba",
                "ARTIKEL": "der",
                "SINGULAR": "Fisch",
                "PLURAL": "Fische",
                "POINTS_WORD": 2,
                "POINTS_ARTICLE": 1
            },
            {
                "PL": "kot",
                "ARTIKEL": "die",
                "SINGULAR": "Katze",
                "PLURAL": "Katzen",
                "POINTS_WORD": 5,
                "POINTS_ARTICLE": 3
            },
            {
                "PL": "dziecko",
                "ARTIKEL": "das",
                "SINGULAR": "Kind",
                "PLURAL": "Kinder",
                "POINTS_WORD": 0,
                "POINTS_ARTICLE": 0
            },
        ]

        n_test=200

        for i, line in enumerate(self.data[n_test:n_test+100]):

            inner_line = BoxLayout(orientation='horizontal',size_hint_y=None)
            button = Button(text="remove", size_hint_x=0.3)
            label = Label(
                text=f"{i+n_test}: [b]{line['PL']}[/b]\n {line['ARTIKEL']} | {line['SINGULAR']}\nPunkty: {line['POINTS_WORD']} ",
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
            inner_layout.add_widget(inner_line)
        scroll.add_widget(inner_layout)
        content.add_widget(scroll)

        new_word_btn = Button(text="new word", size_hint=(1, 0.1))
        content.add_widget(new_word_btn)
        new_word_btn.bind(on_press=self.new_word_popup)

        close_btn = Button(text="close word list", size_hint=(1, 0.1))
        content.add_widget(close_btn)
        close_btn.bind(on_press=lambda x: popup.dismiss())
        popup = Popup(
            title="word list",
            content=content,
            size_hint=(1, 1),
            auto_dismiss=False  # nie zamykaj po kliknięciu w tło
        )

        popup.open()

    def new_word_popup(self, instance):
        # zawartość okienka
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        new_word_btn = Button(text="new word", size_hint=(1, 0.1))
        content.add_widget(new_word_btn)
        new_word_btn.bind(on_press=self.new_word_popup)

        close_btn = Button(text="cancel", size_hint=(1, 0.1))
        content.add_widget(close_btn)
        close_btn.bind(on_press=lambda x: popup.dismiss())
        popup = Popup(
            title="word list",
            content=content,
            size_hint=(1, 1),
            auto_dismiss=False  # nie zamykaj po kliknięciu w tło
        )

        popup.open()

class NomenApp(App):
    def build(self):
        self.main_widget = Nomen()
        return self.main_widget

    def on_stop(self):
        """Zapisz dane po zamknięciu aplikacji"""
        self.main_widget.save_data(self.main_widget.data)
        print("✅ Dane zapisane do pliku data.csv przed zamknięciem.")


if __name__ == "__main__":
    NomenApp().run()
