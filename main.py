import os
import pandas as pd
import plotly.express as px
from flask import Flask, request, render_template, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from sectors import SECTOR_COLUMNS  # Імпорт даних про сфери

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Функція для перевірки, чи дозволений формат файлу
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Головна сторінка для вибору сфери та завантаження файлу
@app.route('/', methods=['GET'])
def upload_page():
    return render_template('upload.html')

# Обробка вибору сфери та надання відповідних стовпців
@app.route('/get_sector_columns', methods=['POST'])
def get_sector_columns():
    sector = request.json.get('sector')
    columns = SECTOR_COLUMNS.get(sector, [])
    return jsonify(columns=columns)

# Завантаження файлу після вибору сфери
@app.route('/upload', methods=['POST'])
def upload_file():
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
    return 'Invalid file format'

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
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
