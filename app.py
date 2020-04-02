#!flask/bin/python
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from pdfparser import parse
from hmatrix import max_h_plot
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest
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
		raise BadRequest('No file found')
	
	file = request.files['file']
	if not is_pdf(file.filename):
		raise BadRequest('Not a PDF file')
	
	# save pdf file locally
	path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
	file.save(path)

	try:
		# parse local pdf file
		properties = parse(path)
		return jsonify(properties)
	except:
		raise BadRequest('Error parsing file. Please try again')
	finally:
		# delete local file
		os.remove(path)
	

@app.route('/graph', methods=['POST'])
def matrix():
	print(json.loads(request.data))
	return jsonify(max_h_plot(json.loads(request.data)))

def is_pdf(filename):
	return '.' in filename and filename.split('.', 1)[1].lower() == 'pdf'

if __name__ == '__main__':
    app.run()