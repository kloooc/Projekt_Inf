import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import PySimpleGUI as sg
import os
import urllib.request
import io

# Function to load data from a file
def load_data():
    layout = [
        [sg.Text('Select data file:', font=('Helvetica', 12))],
        [sg.Input(), sg.FileBrowse()],
        [sg.Button('Continue with standard data'), sg.OK(), sg.Cancel()]
    ]
    window = sg.Window('Load Data File', layout)
    event, values = window.read()
    window.close()
    if event == 'OK':
        filename = values[0]
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename, delimiter=';')
                return df
            except:
                sg.popup_error('Error loading the file!')
        else:
            sg.popup_error('File does not exist!')
    elif event == 'Continue with standard data':
        filename = 'winequality-white.csv'  # Enter the file name if different
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename, delimiter=';')
                return df
            except:
                sg.popup_error('Error loading the file!')
        else:
            sg.popup_error('File does not exist!')

# Load the data
df = load_data()
if df is None:
    exit()

# Function to compute statistical measures for a selected column
def compute_stats(column):
    return [df[column].min(), df[column].max(), df[column].std(), df[column].median(), df[column].mode()[0]]


# Function to compute correlations between features
def compute_correlation():
    selected_features = values['-LIST-']
    if len(selected_features) == 1:
        feature = selected_features[0]
        corr = df.corr()[feature]
        plt.figure(figsize=(12, 10))
        plt.bar(corr.index, corr.values)
        plt.title('Correlation with {}'.format(feature))
        plt.xticks(rotation=90)
        plt.show()
    elif len(selected_features) == 2:
        feature1, feature2 = selected_features
        corr = df[[feature1, feature2]].corr()
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, fmt='.3f')
        plt.title('Feature Correlation')
        plt.show()
    elif len(selected_features) > 2:
        corr = df.corr()
        plt.figure(figsize=(15, 12))  # Adjust the figsize as per your preference
        sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, fmt='.3f')
        plt.title('Feature Correlation')
        plt.show()
    else:
        sg.popup_error('Please select at least one feature.')

def compute_correlations():
    corr = df.corr()
    plt.figure(figsize=(11, 8))
    sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, fmt='.3f')
    plt.title('Feature Correlation')
    plt.show()

# Function to display statistical measures in a new window
def display_stats(selected_features):
    layout = [
        [sg.Multiline('', size=(60, 10), key='-OUTPUT-', disabled=True, autoscroll=True)],
        [sg.Button('OK', font=('Helvetica', 12))]
    ]
    window = sg.Window('Statistical Measures Results', layout, finalize=True)

    output = ""
    for feature in selected_features:
        stats = compute_stats(feature)
        output += 'Statistical measures for feature {}:'.format(feature) + '\n'
        output += 'Minimum: {}\n'.format(stats[0])
        output += 'Maximum: {}\n'.format(stats[1])
        output += 'Standard Deviation: {}\n'.format(stats[2])
        output += 'Median: {}\n'.format(stats[3])
        output += 'Mode: {}\n\n'.format(stats[4])

    window['-OUTPUT-'].update(output)

    while True:
        event, _ = window.read()
        if event == sg.WIN_CLOSED or event == 'OK':
            break

    window.close()


# Create the GUI
sg.theme('DarkBlue3')
layout = [
    [sg.Text('Select feature:', font=('Helvetica', 12))],
    [sg.Listbox(df.columns[:-1], size=(30, 6), key='-LIST-', enable_events=True, select_mode='extended')],
    [sg.Button('Display Statistical Measures', font=('Helvetica', 12), disabled=True, key='-STATS-')],
    [sg.Button('Display Correlation', font=('Helvetica', 12), disabled=True, key='-CORRELATION-')],
    [sg.Button('Display All Correlations', font=('Helvetica', 12), disabled=False, key='-ALL_CORRELATIONS-')],
    [sg.Button('Exit', font=('Helvetica', 12))]
]

window = sg.Window('Data Analysis', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    elif event == '-LIST-':
        window['-STATS-'].update(disabled=False)
        window['-CORRELATION-'].update(disabled=False)
        window['-ALL_CORRELATIONS-'].update(disabled=False)
    elif event == '-STATS-':
        selected_features = values['-LIST-']
        if selected_features:
            display_stats(selected_features)
    elif event == '-CORRELATION-':
        selected_features = values['-LIST-']
        if len(selected_features) == 1 or len(selected_features) == 2:
            compute_correlation()
        else:
            sg.popup_error('Please select either one or two features.')
    elif event == '-ALL_CORRELATIONS-':
        compute_correlations()

window.close()
