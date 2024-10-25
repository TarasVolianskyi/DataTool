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
    # Описова статистика
    description = data.describe(include='all').to_html()

    # Визначення ключових показників
    total_stores = len(data['Store'].unique()) if 'Store' in data.columns else 'N/A'
    total_sales = data['Sales'].sum() if 'Sales' in data.columns else 'N/A'
    total_profit = data['Profit'].sum() if 'Profit' in data.columns else 'N/A'
    margin_percentage = (total_profit / total_sales * 100) if total_sales != 'N/A' and total_sales > 0 else 'N/A'
    total_orders = len(data) if 'Order ID' in data.columns else 'N/A'
    return_percentage = (data['Returns'].mean() * 100) if 'Returns' in data.columns else 'N/A'

    # Побудова графіків для аналізу
    visualizations = []

    # Діаграма продажів по категоріях товарів
    if 'Product Category' in data.columns and 'Sales' in data.columns:
        fig = px.bar(data.groupby('Product Category')['Sales'].sum().reset_index(),
                     x='Product Category', y='Sales', title='Sales by Category')
        graph_path = os.path.join('static', 'sales_by_category_plot.html')
        fig.write_html(graph_path)
        visualizations.append('sales_by_category_plot.html')

    # Діаграма продажів по магазинах
    if 'Store' in data.columns and 'Sales' in data.columns:
        fig = px.bar(data.groupby('Store')['Sales'].sum().reset_index(),
                     x='Store', y='Sales', title='Sales by Store')
        graph_path = os.path.join('static', 'sales_by_store_plot.html')
        fig.write_html(graph_path)
        visualizations.append('sales_by_store_plot.html')

    # Передача змінних у шаблон
    return render_template('analysis.html',
                           data=data,
                           total_stores=total_stores,
                           total_sales=total_sales,
                           total_profit=total_profit,
                           margin_percentage=margin_percentage,
                           total_orders=total_orders,
                           return_percentage=return_percentage,
                           graphs=visualizations)

if __name__ == '__main__':
    # Створення папки для завантажень, якщо вона не існує
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
