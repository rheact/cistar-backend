#!flask/bin/python
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from pdfparser import parse
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/home/samk/Projects/cistar-backend'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
	a = task_id+1
	print(a)

	return jsonify({'a':a})

@app.route('/pdf', methods=['POST'])
def p():
	if 'file' not in request.files:
		return jsonify("No file found")
	
	file = request.files['file']
	if not is_pdf(file.filename):
		return("Not a PDF file")
	
	
	# save pdf file locally
	path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
	file.save(path)

	# parse local pdf file
	a = parse(path)

	# delete local file
	os.remove(path)
	return jsonify({'a': a})
	

def is_pdf(filename):
	return '.' in filename and filename.split('.', 1)[1].lower() == 'pdf'

if __name__ == '__main__':
    app.run()