#!flask/bin/python
# -*- coding: utf-8 -*-
import json

from flask import Flask, jsonify, request, make_response, send_from_directory, safe_join
from flask_cors import CORS
from sds.parser import parse
from cameo.crawler import cameo_selenium_export, init_driver
from calculation_block.calculation_block import calculate_cp_mix, calculate_without_cp_mix, extract_properties, cp
from hmatrix import max_h_plot
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest

@app.route('/calculate', methods=['POST'])
def calculate():
	try:
		data = json.loads(request.data)
		operatingParams = data['operatingParams']
		reactants = data['reactants']
		products = data['products']
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
