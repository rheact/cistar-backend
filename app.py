#!flask/bin/python
# -*- coding: utf-8 -*-
import os
import json
import math
import uuid
import ast
from subprocess import call

from flask import Flask, jsonify, request, make_response, send_file, send_from_directory, safe_join
from flask_cors import CORS
from parse.pdfparser import parse
from parse.cameo_selenium_export import cameo_selenium_export
from calculation_block.calculation_block import calculate_cp_mix, calculate_without_cp_mix, extract_properties, cp
from hmatrix import max_h_plot
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest

UPLOAD_FOLDER = os.getcwd()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORT_FOLDER'] = UPLOAD_FOLDER + '/reports'
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return "Hello, World!"

# set up error handler
@app.errorhandler(BadRequest)
def handle_exception(e):
	# taken from https://flask.palletsprojects.com/en/1.1.x/errorhandling/
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "error": e.description
    })
    response.content_type = "application/json"
    return response

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

	# calculate cp
	temperature = request.args.get('temperature')
	properties['cp'] = cp(cas_no, temperature)

	# parse properties from second database
	try:
		additional_properties = extract_properties(cas_no)
		coerce_properties(properties, additional_properties)
	except Exception as e:
		raise BadRequest('Unable to get properties from second database')
	
	return jsonify(properties)

@app.route('/calculate', methods=['POST'])
def calculate():
	try:
		data = json.loads(request.data)
		operatingParams = data['operatingParams']
		reactants = data['reactants']
		products = data['products']
		print(operatingParams)
		# operatingParams have been validated on frontend
		heat_of_reaction = float(operatingParams['heatOfReaction'])
		temperature = float(operatingParams['temperature'])
		pressure = float(operatingParams['pressure'])
		if operatingParams['cp'] != '':
			cp = float(operatingParams['cp'])
			calculation_block = calculate_cp_mix(heat_of_reaction, cp, temperature, pressure)
		else:
			calculation_block = calculate_without_cp_mix(reactants, products, heat_of_reaction, temperature, pressure)
	except Exception as e:
		raise BadRequest('Unable to compute calculation block')

	print(calculation_block)
	return jsonify(calculation_block)
		

@app.route('/graph', methods=['POST'])
def matrix():
	try:
		return jsonify(max_h_plot(request.data.decode('utf-8')))
	except Exception as e:
		raise BadRequest('Unable to create H-Matrix')

@app.route('/cameo', methods=['POST'])
def cameo():
	data = json.loads(request.data)
	
	try:
		response = make_response(jsonify(cameo_selenium_export(data['reactants'] + data['products'] + data['diluents'])))
		response.headers["Access-Control-Allow-Origin"] = '*'
		#headers: {'Access-Control-Allow-Origin': '*'}
		return response
	except Exception as e:
		print('exception: ', e)
		raise BadRequest('Unable to create Cameo Table')

@app.route('/save', methods=['POST'])
def save():
	try:
		html = ast.literal_eval(request.data.decode('utf-8'))['data']
		id = str(uuid.uuid4())

		filename = 'report-{}'.format(id)
		path = safe_join(app.config['REPORT_FOLDER'], filename)
		with open('{}.html'.format(path), 'w') as html_file:
			html_file.write(html)
		
		# transform this html to pdf
		call(['wkhtmltopdf', '--encoding', 'utf-8', '{}.html'.format(path), '{}.pdf'.format(path)])
		response = send_from_directory(app.config['REPORT_FOLDER'], '{}.pdf'.format(filename), as_attachment=True)

		# clean up temporary files
		os.remove('{}.html'.format(path))
		os.remove('{}.pdf'.format(path))

		return response 
	except Exception as e:
		print('exception: ', e)
		raise BadRequest('Unable to create Cameo Table')
		return {}

# if a property was not contained in the SDS and retreived with parse(), however does exist
# in the second database, we'll replace that value in properties with the value from
# the second database
def coerce_properties(properties, additional_properties):
	# relevant properties we're dealing with
	props = ['boilingPt', 'flashPt', 'autoIgnitionTemp', 'upperExplosionLim', 'lowerExplosionLim']
	for prop in props:
		if properties[prop] == 'No data available' and math.isnan(additional_properties[prop]) is False:
			properties[prop] = additional_properties[prop]

def is_pdf(filename):
	return '.' in filename and filename.split('.', 1)[1].lower() == 'pdf'

if __name__ == '__main__':
    app.run()
