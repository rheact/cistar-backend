#!flask/bin/python
import os
import json
import math

from flask import Flask, jsonify, request
from flask_cors import CORS
from parse.pdfparser import parse
from calculation_block.calculation_block import extract_properties, cp
from hmatrix import max_h_plot
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest

UPLOAD_FOLDER = os.getcwd()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/pdf', methods=['POST'])
def file_upload():
	if 'file' not in request.files:
		raise BadRequest('No file found')
	
	file = request.files['file']
	if not is_pdf(file.filename):
		raise BadRequest('Not a PDF file')
	
	# save pdf file locally
	path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
	file.save(path)

	# parse local pdf file
	try:
		properties = parse(path)
	except:
		raise BadRequest('Error parsing file. Please try again')
	finally:
		# delete local file
		os.remove(path)
	
	cas_no = properties['casNo']

	# calculate cp (reactant only)
	temperature = request.args.get('temperature')
	if temperature is not None:
		properties['cp'] = cp(cas_no, temperature)

	# parse properties from second database
	try:
		additional_properties = extract_properties(cas_no)
		coerce_properties(properties, additional_properties)
	except Exception as e:
		raise BadRequest('Unable to get properties from second database')
	
	return jsonify(properties)
	

@app.route('/graph', methods=['POST'])
def matrix():
	print(json.loads(request.data))
	return jsonify(max_h_plot(json.loads(request.data)))

# if a property was not contained in the SDS and retreived with parse(), however does exist
# in the second database, we'll replace that value in properties with the value from
# the second database
def coerce_properties(properties, additional_properties):
	# relevant properties we're dealing with
	props = ['boilingPt', 'flashPt', 'autoIgnitionTemp']
	for prop in props:
		if properties[prop] == 'No data available' and math.isnan(additional_properties[prop]) is False:
			properties[prop] = additional_properties[prop]

def is_pdf(filename):
	return '.' in filename and filename.split('.', 1)[1].lower() == 'pdf'

if __name__ == '__main__':
    app.run()