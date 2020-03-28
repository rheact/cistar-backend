#!flask/bin/python
import os
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from pdfparser import parse
from hmatrix import max_h_plot
from werkzeug.utils import secure_filename
import json

UPLOAD_FOLDER = os.getcwd()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app, resources={r"/*": {"origins": "*"}})

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
	properties = parse(path)

	# delete local file
	os.remove(path)
	return jsonify(properties)

@app.route('/graph', methods=['POST'])
def matrix():
	print(json.loads(request.data))
	return jsonify(max_h_plot(json.loads(request.data)))

def is_pdf(filename):
	return '.' in filename and filename.split('.', 1)[1].lower() == 'pdf'

if __name__ == '__main__':
    app.run()