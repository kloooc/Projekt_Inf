import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import PySimpleGUI as sg
import os
import urllib.request
import io

# Funkcja do wczytania pliku z danymi
def load_data():
    layout = [
        [sg.Text('Wybierz plik z danymi:', font=('Helvetica', 12))],
        [sg.Input(), sg.FileBrowse()],
        [sg.Button('Kontynuuj ze standardowymi danymi'), sg.OK(), sg.Cancel()]
    ]
    window = sg.Window('Wczytaj plik z danymi', layout)
    event, values = window.read()
    window.close()
    if event == 'OK':
        filename = values[0]
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename, delimiter=';')
                return df
            except:
                sg.popup_error('Błąd wczytywania pliku!')
        else:
            sg.popup_error('Plik nie istnieje!')
    elif event == 'Kontynuuj ze standardowymi danymi':
        url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-white.csv'
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read().decode('utf-8')
                df = pd.read_csv(io.StringIO(data), delimiter=';')
                return df
        except:
            sg.popup_error('Błąd pobierania danych standardowych!')
    return None

# Wczytanie danych
df = load_data()
if df is None:
    exit()

# Funkcja do obliczenia miar statystycznych dla wybranej kolumny
def compute_stats(column):
    return [df[column].min(), df[column].max(), df[column].std(), df[column].median(), df[column].mode()[0]]


# Funkcja do wyznaczania korelacji między cechami
def compute_correlation():
    corr = df.corr()
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title('Korelacja cech')
    plt.show()


# Tworzenie GUI
sg.theme('DarkBlue3')
layout = [
    [sg.Text('Wybierz cechę:', font=('Helvetica', 12))],
    [sg.Listbox(df.columns[:-1], size=(30, 6), key='-LIST-', enable_events=True)],
    [sg.Button('Wyświetl miary statystyczne', font=('Helvetica', 12), disabled=True, key='-STATS-')],
    [sg.Button('Wyświetl korelację', font=('Helvetica', 12), disabled=True, key='-CORRELATION-')],
    [sg.Button('Wyjdź', font=('Helvetica', 12))]
]

window = sg.Window('Analiza danych', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Wyjdź':
        break
    elif event == '-LIST-':
        window['-STATS-'].update(disabled=False)
        window['-CORRELATION-'].update(disabled=False)
    elif event == '-STATS-':
        selected_feature = values['-LIST-'][0]
        stats = compute_stats(selected_feature)
        sg.popup('Miary statystyczne dla cechy {}:'.format(selected_feature), 'Minimum: {}'.format(stats[0]),
                 'Maksimum: {}'.format(stats[1]), 'Odchylenie standardowe: {}'.format(stats[2]),
                 'Mediana: {}'.format(stats[3]), 'Moda: {}'.format(stats[4]))
    elif event == '-CORRELATION-':
        compute_correlation()

window.close()