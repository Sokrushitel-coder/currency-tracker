import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from src.api import get_exchange_rate


MONTHS = ["", "Янв", "Фев", "Мар", "Апр", "Май", "Июн",
          "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]


def get_dates_by_scale(scale: str) -> list[str]:
    """Возвращает список дат для выпадающего списка в зависимости от масштаба."""
    end_date = datetime.now()
    dates = []
    start_date = end_date - timedelta(days=3650)

    step = {
        "Неделя": timedelta(days=7),
        "Месяц": relativedelta(months=+1),
        "Квартал": relativedelta(months=+3),
        "Год": relativedelta(months=+12),
    }.get(scale, timedelta(days=7))

    while start_date <= end_date:
        dates.append(start_date.strftime("%d.%m.%Y"))
        start_date += step

    return dates


def build_graph_data(currency: str, scale: str, selected_date: str):
    """Собирает данные для графика: даты и значения курса."""
    start_date = datetime.strptime(selected_date, "%d.%m.%Y")
    dates = []
    values = []

    if scale == "Неделя":
        end_date = start_date + timedelta(days=7)
        step = timedelta(days=1)
    elif scale == "Месяц":
        end_date = start_date + timedelta(days=30)
        step = timedelta(days=3)
    elif scale == "Квартал":
        end_date = start_date + relativedelta(months=+3)
        step = timedelta(days=9)
    else:  # Год
        end_date = start_date + relativedelta(months=+12)
        step = relativedelta(months=+1)
        start_date += relativedelta(months=+1)

    current = start_date
    while current <= end_date:
        date_str = current.strftime("%d/%m/%Y")
        try:
            rates = get_exchange_rate(date_str)
            if currency == "RUB":
                values.append(1)
            else:
                values.append(rates.get(currency, 0))
        except Exception:
            values.append(0)

        if scale == "Год":
            dates.append(MONTHS[int(current.strftime("%m"))])
        else:
            dates.append(current.strftime("%d.%m.%Y"))

        current += step

    return dates, values


def create_figure(currency: str, scale: str, dates: list, values: list):
    """Создаёт фигуру matplotlib с графиком."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(dates, values)

    if scale.lower() == "неделя":
        title = f"Динамика курса {currency} за неделю"
    else:
        title = f"Динамика курса {currency} за {scale.lower()}"

    ax.set(xlabel="Дата", ylabel="Курс", title=title)
    ax.grid()

    if scale in ("Неделя", "Месяц"):
        plt.xticks(rotation=45)
    else:
        plt.xticks(rotation=90)

    plt.tight_layout()
    return fig


def draw_graph_on_canvas(fig, parent):
    """Встраивает график в Tkinter-виджет."""
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack()
    return canvas
