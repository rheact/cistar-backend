#!flask/bin/python
from flask import Flask, jsonify
from pdfparser import parse

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
	a = task_id+1
	print(a)

	return jsonify({'a':a})


@app.route('/pdf/<path:f_name>', methods=['GET'])
def p(f_name):
	
	a = parse(f_name)

	return jsonify({'a':a})

if __name__ == '__main__':
    app.run()