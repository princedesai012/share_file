from flask import Flask, request, send_file, render_template, url_for
from pyngrok import ngrok  # Import pyngrok
import os
import uuid
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory storage for uploaded files
file_db = {}

# Helper function to validate file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Check if a file is present in the request
        if 'file' not in request.files:
            return "No file part in the request", 400

        file = request.files['file']
        if file.filename == '':
            return "No file selected", 400

        # Validate file type
        if not allowed_file(file.filename):
            return f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}", 400

        # Secure filename and save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Generate a unique token
        token = str(uuid.uuid4())
        file_db[token] = file_path

        # Generate shareable download link
        shareable_link = url_for('download_file', token=token, _external=True)
        return f"File uploaded successfully! Shareable link: <a href='{shareable_link}'>{shareable_link}</a>"

    except Exception as e:
        print(f"Error during file upload: {e}")
        return "An error occurred during file upload.", 500

@app.route('/download/<token>')
def download_file(token):
    try:
        # Check if the token exists
        if token not in file_db:
            return "File not found", 404

        file_path = file_db[token]

        # Verify file existence
        if not os.path.exists(file_path):
            return "File no longer exists on the server", 404

        # Send file to the user
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        print(f"Error during file download: {e}")
        return "An error occurred during file download.", 500

if __name__ == '__main__':
    # Set your ngrok authentication token
    ngrok.set_auth_token("2rqwWbtp4erzKJWSVYgzzR101ca_58tmPhLXPsvK7pNu9CKSs")  # Replace with your ngrok auth token

    # Start ngrok tunnel
    public_url = ngrok.connect(5000).public_url
    print(f" * ngrok tunnel started! Public URL: {public_url}")

    # Run Flask app
    app.run(port=5000)
