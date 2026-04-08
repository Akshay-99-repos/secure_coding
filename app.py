from flask import Flask, request, render_template, jsonify
import os
import tempfile
import subprocess

app = Flask(__name__)


# Home page with upload form
@app.route('/', methods=['GET'])
def index():
    return '''
    <h2>Upload a file to scan for vulnerabilities</h2>
    <form method="post" action="/scan" enctype="multipart/form-data">
        <input type="file" name="file" />
        <input type="submit" value="Scan" />
    </form>
    '''

# Endpoint to handle file upload, scan for vulnerabilities, and show results
@app.route('/scan', methods=['POST'])
def scan():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    content = file.read().decode(errors='ignore')

    # Save file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(content.encode())
        tmp_path = tmp.name

    # Run semgrep on the file
    try:
        result = subprocess.run([
            'semgrep',
            '--config', 'auto',
            tmp_path
        ], capture_output=True, text=True, timeout=60)
        output = result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        output = f"Error running semgrep: {e}"
    finally:
        os.unlink(tmp_path)

    return f'<h3>Vulnerability Scan Results:</h3><pre>{output[:5000]}</pre>'

if __name__ == '__main__':
    app.run(debug=True)
