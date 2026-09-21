import os
import tempfile
from flask import Flask, request, render_template, send_file, jsonify
from converter import convert_py_to_pdf, convert_ipynb_to_pdf

app = Flask(__name__)

# Ensure the app can handle larger uploads if needed, 16MB max
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = file.filename
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if ext not in ['py', 'ipynb']:
        return jsonify({'error': 'Unsupported file type. Please upload .py or .ipynb files.'}), 400
    
    try:
        content = file.read().decode('utf-8')
        
        # Create a temporary file for the output PDF
        fd, pdf_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        
        if ext == 'py':
            convert_py_to_pdf(content, pdf_path)
        elif ext == 'ipynb':
            convert_ipynb_to_pdf(content, pdf_path)
            
        # Return the generated PDF to the user
        return send_file(
            pdf_path, 
            as_attachment=True, 
            download_name=f"{filename.rsplit('.', 1)[0]}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'An error occurred during conversion: {str(e)}'}), 500

if __name__ == '__main__':
    # In production, use Gunicorn instead of this dev server
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
