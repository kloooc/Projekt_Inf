import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import PySimpleGUI as sg
import openpyxl
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
                symbolic_columns = []
                for column in df.columns:
                    if df[column].dtype == 'object':
                        symbolic_columns.append(column)
                if symbolic_columns:
                    df[symbolic_columns] = df[symbolic_columns].astype('object')  # Convert symbolic columns to object type
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
                symbolic_columns = []
                for column in df.columns:
                    if df[column].dtype == 'object':
                        symbolic_columns.append(column)
                if symbolic_columns:
                    df[symbolic_columns] = df[symbolic_columns].astype('object')  # Convert symbolic columns to object type
                return df
            except:
                sg.popup_error('Error loading the file!')
        else:
            sg.popup_error('File does not exist!')


# Load the data
df = load_data()
if df is None:
    exit()

def display_bar_plot(column):
    plt.figure(figsize=(12, 8))
    plt.xticks(rotation=60, ha='right', fontsize=6)
    sns.countplot(x=column, data=df)
    plt.title('Bar Plot for {}'.format(column))
    plt.xlabel(column)
    plt.ylabel('Count')
    plt.tight_layout()  # Poprawa rozmieszczenia etykiet
    plt.show()

# Function to compute statistical measures for a selected column
def compute_stats(column):
    return [df[column].min(), df[column].max(), df[column].std(), df[column].median(), df[column].mode()[0]]

def display_histogram(column):
    plt.figure(figsize=(8, 6))
    plt.hist(df[column], bins=10, color='green')
    plt.title('Histogram for {}'.format(column))
    plt.xlabel(column)
    plt.ylabel('Frequency')
    plt.show()

def scatter_plot():
    elected_features = values['-LIST-']
    if len(selected_features) == 2:
        feature1, feature2 = selected_features
        plt.figure(figsize=(8, 6))
        plt.scatter(df[feature1], df[feature2])
        plt.title('Scatter Plot: {} vs {}'.format(feature1, feature2))
        plt.xlabel(feature1)
        plt.ylabel(feature2)
        plt.show()
    else:
        sg.popup_error('Please select at least one feature.')

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
        plt.figure(figsize=(7, 4))
        sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, fmt='.3f')
        plt.title('Feature Correlation')
        plt.show()
    else:
        sg.popup_error('Please select at least one feature.')


def export_data():
    data2 = df.values.tolist()
    headers = df.columns.tolist()
    layout = [
        [sg.Table(values=data2, headings=headers, max_col_width=25,
                  auto_size_columns=True, display_row_numbers=True,
                  justification='left', num_rows=min(25, len(data2)))],
        [sg.Text('Select columns to export:', font=('Helvetica', 12))],
        [sg.Listbox(df.columns[:-1], size=(30, 6), key='-EXPORT-COLUMNS-', select_mode='multiple')],
        [sg.Text('Select row range to export:', font=('Helvetica', 12))],
        [sg.InputText('1', key='-EXPORT-START-'), sg.Text('to'), sg.InputText(str(len(df)), key='-EXPORT-END-')],
        [sg.Button('Export', font=('Helvetica', 12)), sg.Button('Cancel', font=('Helvetica', 12))]
    ]
    window = sg.Window('Export Data', layout)
    event, values = window.read()
    window.close()

    if event == 'Export':
        selected_columns = values['-EXPORT-COLUMNS-']
        start_row = int(values['-EXPORT-START-'])
        end_row = int(values['-EXPORT-END-'])

        if selected_columns:
            export_df = df[selected_columns][start_row - 1:end_row]
            export_filename = sg.popup_get_file('Save As', save_as=True, default_extension='.xlsx',
                                                file_types=(('Excel Files', '*.xlsx'),))

            if export_filename:
                export_df.to_excel(export_filename, index=False)
                sg.popup('Data successfully exported to Excel file!')
        else:
            sg.popup_error('Please select at least one column to export.')


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
    [sg.Text('Select feature: \nHold ctrl / shift to select multiple features', font=('Helvetica', 12))],
    [sg.Listbox(df.columns[:-1], size=(30, 6), key='-LIST-', enable_events=True, select_mode='extended')],
    [sg.Button('Display Statistical Measures', font=('Helvetica', 12), disabled=True, key='-STATS-'),
     sg.Button('Display Histogram', font=('Helvetica', 12), disabled=True, key='-HISTOGRAM-')],
    [sg.Button('Display Correlation', font=('Helvetica', 12), disabled=True, key='-CORRELATION-'),
     sg.Button('Display Scatter Plot', font=('Helvetica', 12), disabled=True, key='-scatter_plot-')],
    [sg.Button('Export Data', font=('Helvetica', 12), key='Export_Data'),
     sg.Button('Display Bar Plot', font=('Helvetica', 12), disabled=True, key='-BAR_PLOT-')],
    [sg.Button('Display All Correlations', font=('Helvetica', 12), disabled=False, key='-ALL_CORRELATIONS-')],
    [sg.Button('Exit', font=('Helvetica', 12))]
]

window = sg.Window('Data Analysis', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    elif event == '-LIST-':
        selected_features = values['-LIST-']
        if len(selected_features) == 1:
            window['-STATS-'].update(disabled=False)
            window['-HISTOGRAM-'].update(disabled=False)
            window['-CORRELATION-'].update(disabled=False)
            window['-scatter_plot-'].update(disabled=True)
            window['-BAR_PLOT-'].update(disabled=False)
            window['-ALL_CORRELATIONS-'].update(disabled=False)
        elif len(selected_features) == 2:
            window['-STATS-'].update(disabled=True)
            window['-HISTOGRAM-'].update(disabled=True)
            window['-CORRELATION-'].update(disabled=False)
            window['-scatter_plot-'].update(disabled=False)
            window['-BAR_PLOT-'].update(disabled=True)
            window['-ALL_CORRELATIONS-'].update(disabled=False)
        else:
            window['-STATS-'].update(disabled=True)
            window['-HISTOGRAM-'].update(disabled=True)
            window['-CORRELATION-'].update(disabled=True)
            window['-scatter_plot-'].update(disabled=True)
            window['-BAR_PLOT-'].update(disabled=True)
            window['-ALL_CORRELATIONS-'].update(disabled=False)
    elif event == '-STATS-':
        selected_features = values['-LIST-']
        if selected_features:
            display_stats(selected_features)
    elif event == '-HISTOGRAM-':
        selected_features = values['-LIST-']
        if len(selected_features) == 1:
            display_histogram(selected_features[0])
        else:
            sg.popup_error('Please select only one feature.')
    elif event == '-scatter_plot-':
        selected_features = values['-LIST-']
        if len(selected_features) == 2:
            scatter_plot()
        else:
            sg.popup_error('Please select only two feature.')
    elif event == '-CORRELATION-':
        selected_features = values['-LIST-']
        if len(selected_features) == 1 or len(selected_features) == 2:
            compute_correlation()
        else:
            sg.popup_error('Please select either one or two features.')
    elif event == '-ALL_CORRELATIONS-':
        compute_correlations()
    elif event == 'Export_Data':
        export_data()
    elif event == '-BAR_PLOT-':
        selected_features = values['-LIST-']
        if len(selected_features) == 1:
            display_bar_plot(selected_features[0])
        else:
            sg.popup_error('Please select only one feature.')

window.close()
