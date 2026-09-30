import tkinter as tk
import tkinter.ttk as ttk

from src.api import get_currency_list, get_today_rate
from src.graph import get_dates_by_scale, build_graph_data, create_figure, draw_graph_on_canvas


class CurrencyApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Конвертер валют и график курса")

        self.scale_var = tk.StringVar(value="Неделя")
        self.result_var = tk.StringVar()

        self._build_tabs()
        self._build_converter_tab()
        self._build_graph_tab()
        self._load_currencies()

        self._center_window(800, 650)

    # ---------- Построение интерфейса ----------

    def _build_tabs(self):
        self.tab_control = ttk.Notebook(self.root)
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab1, text="Конвертер валют")
        self.tab_control.add(self.tab2, text="График курса")
        self.tab_control.pack(expand=1, fill="both")

    def _build_converter_tab(self):
        tk.Label(self.tab1, text="Исходная валюта:").pack()
        self.combobox_from = ttk.Combobox(self.tab1)
        self.combobox_from.pack()

        tk.Label(self.tab1, text="Целевая валюта:").pack()
        self.combobox_to = ttk.Combobox(self.tab1)
        self.combobox_to.pack()

        tk.Label(self.tab1, text="Сумма:").pack()
        self.entry_amount = tk.Entry(self.tab1)
        self.entry_amount.pack()

        tk.Label(self.tab1, textvariable=self.result_var).pack()

        tk.Button(self.tab1, text="Конвертировать",
                  command=self.convert_currency).pack()

    def _build_graph_tab(self):
        tk.Label(self.tab2, text="Валюта:").pack()
        self.combobox_currency = ttk.Combobox(self.tab2)
        self.combobox_currency.pack()

        frame_scale = tk.Frame(self.tab2)
        frame_scale.pack()

        tk.Label(frame_scale, text="Масштаб:").pack(side="left")

        for text, value in [("Неделя", "Неделя"), ("Месяц", "Месяц"),
                            ("Квартал", "Квартал"), ("Год", "Год")]:
            tk.Radiobutton(frame_scale, text=text, variable=self.scale_var,
                           value=value, command=self.update_period_values).pack(side="left")

        tk.Label(self.tab2, text="Период c:").pack()
        self.combobox_period = ttk.Combobox(self.tab2)
        self.combobox_period.pack()

        tk.Button(self.tab2, text="Построить график",
                  command=self.plot_graph).pack()

    def _center_window(self, w, h):
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.root.geometry(f"{w}x{h}+{int(x)}+{int(y)}")

    # ---------- Загрузка данных ----------

    def _load_currencies(self):
        try:
            currency_list = get_currency_list()
        except Exception as e:
            print(f"Ошибка загрузки валют: {e}")
            currency_list = ["RUB", "USD", "EUR"]

        self.combobox_from["values"] = currency_list
        self.combobox_to["values"] = currency_list
        self.combobox_currency["values"] = currency_list

        if len(currency_list) > 14:
            self.combobox_from.current(14)
            self.combobox_currency.current(14)
        else:
            self.combobox_from.current(0)
            self.combobox_currency.current(0)

        self.combobox_to.current(0)
        self.update_period_values()

    # ---------- Логика конвертера ----------

    def convert_currency(self):
        try:
            rates = get_today_rate()
            from_currency = self.combobox_from.get()
            to_currency = self.combobox_to.get()
            amount = float(self.entry_amount.get())

            if from_currency == to_currency:
                result = amount
            elif from_currency == "RUB":
                result = amount / rates[to_currency]
            elif to_currency == "RUB":
                result = amount * rates[from_currency]
            else:
                result = (amount * rates[from_currency]) / rates[to_currency]

            self.result_var.set(f"Результат: {result:.2f} {to_currency}")

        except ValueError:
            self.result_var.set("Ошибка: введите корректную сумму.")
        except Exception as e:
            self.result_var.set(f"Ошибка: {e}")

    # ---------- Логика графика ----------

    def update_period_values(self):
        dates = get_dates_by_scale(self.scale_var.get())
        self.combobox_period["values"] = dates
        if dates:
            self.combobox_period.current(len(dates) - 1)

    def destroy_graph(self):
        for widget in self.tab2.winfo_children():
            if widget.__class__.__name__ == "Canvas":
                widget.destroy()

    def plot_graph(self):
        self.destroy_graph()

        currency = self.combobox_currency.get()
        scale = self.scale_var.get()
        selected_date = self.combobox_period.get()

        try:
            dates, values = build_graph_data(currency, scale, selected_date)
            fig = create_figure(currency, scale, dates, values)
            draw_graph_on_canvas(fig, self.tab2)
        except Exception as e:
            print(f"Ошибка построения графика: {e}")

    # ---------- Запуск ----------

    def run(self):
        self.root.mainloop()
