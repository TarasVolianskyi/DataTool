import os
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Функція для перевірки, чи дозволений формат файлу
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Головна сторінка для завантаження файлу
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Перевірка, чи файл завантажено
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return redirect(url_for('analyze_file', filename=filename))
    return render_template('upload.html')

# Сторінка аналізу завантаженого файлу
@app.route('/analyze/<filename>')
def analyze_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    data = pd.read_csv(file_path)

    # Описова статистика
    description = data.describe(include='all').to_html()

    # Визначення кількості числових колонок
    numeric_columns = len(data.select_dtypes(include=['float64', 'int64']).columns)

    # Побудова графіків
    visualizations = []
    for column in data.select_dtypes(include=['float64', 'int64']).columns:
        fig = px.histogram(data, x=column, title=f'Distribution of {column}')
        graph_path = os.path.join('static', f'{column}_plot.html')
        fig.write_html(graph_path)
        visualizations.append(f'{column}_plot.html')

    # Передача змінних у шаблон
    return render_template('analysis.html',
                           tables=[description],
                           data=data,
                           numeric_columns=numeric_columns,
                           graphs=visualizations)

if __name__ == '__main__':
    # Створення папки для завантажень, якщо вона не існує
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
