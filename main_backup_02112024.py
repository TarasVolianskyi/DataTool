import os
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for
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

    # Передача змінних у шаблон для відображення таблиці
    return render_template('analysis.html', table=data.to_html(index=False))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
