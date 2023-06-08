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
        filename = 'winequality-white.csv'  # Wprowadź nazwę pliku, jeśli jest inna
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename, delimiter=';')
                return df
            except:
                sg.popup_error('Błąd wczytywania pliku!')
        else:
            sg.popup_error('Plik nie istnieje!')

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


# Funkcja do wyświetlania wyników miar statystycznych w nowym oknie
def display_stats(selected_features):
    layout = [
        [sg.Multiline('', size=(60, 10), key='-OUTPUT-', disabled=True, autoscroll=True)],
        [sg.Button('OK', font=('Helvetica', 12))]
    ]
    window = sg.Window('Wyniki miar statystycznych', layout, finalize=True)  # Ustawienie finalized=True

    output = ""
    for feature in selected_features:
        stats = compute_stats(feature)
        output += 'Miary statystyczne dla cechy {}:'.format(feature) + '\n'
        output += 'Minimum: {}\n'.format(stats[0])
        output += 'Maksimum: {}\n'.format(stats[1])
        output += 'Odchylenie standardowe: {}\n'.format(stats[2])
        output += 'Mediana: {}\n'.format(stats[3])
        output += 'Moda: {}\n\n'.format(stats[4])

    window['-OUTPUT-'].update(output)

    while True:
        event, _ = window.read()
        if event == sg.WIN_CLOSED or event == 'OK':
            break

    window.close()


# Tworzenie GUI
sg.theme('DarkBlue3')
layout = [
    [sg.Text('Wybierz cechę:', font=('Helvetica', 12))],
    [sg.Listbox(df.columns[:-1], size=(30, 6), key='-LIST-', enable_events=True, select_mode='extended')],
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
        selected_features = values['-LIST-']
        if selected_features:
            display_stats(selected_features)
    elif event == '-CORRELATION-':
        compute_correlation()

window.close()
