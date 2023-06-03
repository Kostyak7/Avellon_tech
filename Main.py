import os
import pandas as pd
import plotly.graph_objs as go
import plotly.offline as pyo
import tkinter as tk
from tkinter import filedialog, messagebox

class App:
    def __init__(self, master):
        self.master = master
        master.title('Визуализация данных осциллографа')
        master.geometry('500x500')

        # добавление кнопки для выбора файлов
        self.select_files_btn = tk.Button(master, text='Выбрать файлы', command=self.select_files)
        self.select_files_btn.pack(pady=20)

        # добавление кнопки для построения графика
        self.plot_btn = tk.Button(master, text='Построить график', state='disabled', command=self.plot)
        self.plot_btn.pack(pady=20)

        # добавление кнопки для конвертирования файлов
        self.convert_btn = tk.Button(master, text='Обработать данные', state='disabled', command=self.convert)
        self.convert_btn.pack(pady=20)

        # добавление кнопки для поиска максимума амплитуд
        self.max_amp_btn = tk.Button(master, text='Найти максимум амплитуд', state='disabled', command=self.max_amp)
        self.max_amp_btn.pack(pady=20)

        # список выбранных файлов
        self.file_list = []

        # создание объекта для визуализации
        self.fig = go.Figure()

    def select_files(self):
        # запрос пользователю на выбор файлов
        files = filedialog.askopenfilenames()

        if len(files) > 0:
            # сохранение выбранных файлов
            self.file_list = list(files)

            # активация кнопки для конвертации
            # self.convert_btn['state'] = 'normal'

            # активация кнопки для построения графика
            self.plot_btn['state'] = 'normal'

            # активация кнопки для вычисления максимальной амплитуды
            # self.max_amp_btn['state'] = 'normal'

    def max_amp(self):
        df = pd.DataFrame(columns=["A","B","C","D"])

        ind_a, ind_b, ind_c, ind_d = 0, 0, 0, 0
        for file_name in self.file_list:
            data=pd.read_csv(file_name)
            max_amplitude = max([float(y) for y in data['y']])

            if file_name[10] == 'A':
                df.loc[ind_a, "A"] = max_amplitude
                ind_a += 1
            elif file_name[10] == 'B':
                df.loc[ind_b, "B"] = max_amplitude
                ind_b += 1
            elif file_name[10] == 'C':
                df.loc[ind_c, "C"] = max_amplitude
                ind_c += 1
            else:
                df.loc[ind_d, "D"] = max_amplitude
                ind_d += 1

        df.to_csv("wind_data.csv", index=False)

        # деактивация кнопки для вычисления амплитуды
        self.max_amp_btn['state'] = 'disabled'

    def convert(self):
        os.chdir("data")

        # цикл по всем файлам
        for file in self.file_list:
            dataf = pd.read_csv(file, header=None)

            time_base = int(dataf.iloc[0][0][10:-2])
            time_base *= 10 ** (-6)
            data_points = int(dataf.iloc[5][0][12:])
            nbm_sqr = 16
            step = time_base * nbm_sqr / data_points

            steps = [None, None, None, None, None, None ]
            for i in range(data_points):
                steps.append((i-1) * step)
            dataf["Steps"] = steps

            os.chdir("../r_data")
            dataf.to_csv("R_" + file, index = False, header=None)

            os.chdir("../w_data")
            dataf = dataf.drop(index=[0,1,2,3,4,5])
            dataf.loc[5] = ["y","x"]
            dataf = dataf.sort_index()
            dataf.to_csv("W_" + file, index = False, header=None)

            os.chdir("../data")

        os.chdir("..")

        # деактивация кнопки для конвертации
        self.plot_btn['state'] = 'disabled'

    def plot(self):
            # очистка объекта для визуализации
            self.fig = go.Figure()

            max_values = []
            file_names = []
            for file in self.file_list:
                # загрузка данных из csv файла
                data = pd.read_csv(file)
                # добавление трассы (trace) на график
                self.fig.add_trace(go.Scattergl(
                    x=data['x'],  # данные для оси X
                    y=data['y'],  # данные для оси Y
                    mode='lines',  # тип трассы - линии
                    name=os.path.basename(file)  # имя трассы - название файла
                ))
                # вычисление максимума и добавление в соответствующие списки
                max_value = data['y'].max()
                max_values.append(max_value)
                file_names.append(os.path.basename(file))
            # добавление таблицы с максимумами на сам график
            self.fig.add_trace(go.Table(
                header=dict(values=['Файл', 'Максимум'],
                            fill_color='paleturquoise',
                            align='left'),
                cells=dict(values=[file_names, max_values],
                           fill_color='lavender',
                           align='right'
                           ))
            )
            # настройка макета графика
            self.fig.update_layout(
                title='Данные осциллографа',  # заголовок графика
                xaxis_title='Время (сек)',  # название оси X
                yaxis_title='Напряжение (мВ)',  # название оси Y
                margin=dict(l=100, r=100, t=100, b=100),
                height=800,
                width=1100,
                grid=dict(columns=1, rows=2),
                template='plotly_white'
            )
            # настройка расположения таблицы на графике
            self.fig.update_layout(
                {
                    'yaxis': {'domain': [0, 1]},
                    'xaxis': {'domain': [0, 1]},
                    'annotations': [
                        {'text': 'Максимумы',
                         'x': 0, 'y': 4000,
                         'showarrow': False,
                         'font': {'size': 10}
                         }
                    ]
                }
            )

            # сохранение визуализации в формате html
            pyo.plot(self.fig, filename='oscilloscope_data.html')

            # сообщение пользователю об успешном построении графика
            messagebox.showinfo('Успешно', 'График успешно построен. Файл сохранен в текущей директории.')

            # деактивация кнопки для построения графика
            self.plot_btn['state'] = 'disabled'

    # создание главного окна приложения
root = tk.Tk()

    # создание объекта приложения
app = App(root)

    # запуск главного цикла приложения
root.mainloop()