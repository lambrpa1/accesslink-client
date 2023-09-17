from flask import Flask, render_template, request, json

import logging, requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():

    data = json.loads(json.dumps(request.get_json()))
    url = data["url"]
    event = data["event"] 

    if event == "EXERCISE":
      url = url + '?samples=true&zones=true'

    token = '237a056de90ec7bfaba89af19302e391'
    headers = {
        'Accept': 'Application/json', 'Authorization': 'Bearer ' + token
    };

    r = requests.get(url, headers=headers)

    if request.method == 'GET':
        app.logger.debug('PING')
    elif request.method == 'POST':
        app.logger.debug('WEBHOOK: ' + json.dumps(request.get_json()))
        app.logger.debug('url: ' + url)
        app.logger.debug('event: ' + event)

        if event == "EXERCISE":
          entity_id = data['entity_id']
          timestamp = data['timestamp']
          app.logger.debug('entity id ' + entity_id)
          filename = event+"."+timestamp+"."+entity_id
          app.logger.debug('writing file ' + filename)
          with open(filename, "w") as outfile:
            json.dump(r.json(), outfile)
        else:
          date = data['date']
          filename = event+"."+date
          app.logger.debug('writing file ' + filename)
          with open(filename, "w") as outfile:
            json.dump(r.json(), outfile)

    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
