from flask import Flask, render_template, request, json

import logging

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        app.logger.debug('PING')
    elif request.method == 'POST':
        app.logger.debug('WEBHOOK: ' + json.dumps(request.get_json()))
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
