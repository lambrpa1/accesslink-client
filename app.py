from flask import Flask, render_template, request, json

import logging, requests
import hmac, hashlib, base64

app = Flask(__name__)

def verify_webhook(data, hmac_header):
    API_SECRET_KEY = '74b4b6e6-4a31-4f6a-975b-4ed73d94a68a'
    digest = hmac.new(API_SECRET_KEY.encode('utf-8'), data, digestmod=hashlib.sha256).digest()
    computed_hmac = digest.hex().encode('utf-8')

    return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():

    app.logger.debug('Signature created by Polar : ' + request.headers.get('Polar-Webhook-Signature'))
    API_SECRET_KEY = '74b4b6e6-4a31-4f6a-975b-4ed73d94a68a'
    digest = hmac.new(API_SECRET_KEY.encode('utf-8'), request.get_data(), digestmod=hashlib.sha256).digest()
    app.logger.debug('Calculated signature       : ' + digest.hex())	
	
    verified = verify_webhook(request.get_data(), request.headers.get('Polar-Webhook-Signature'))

    if verified:
       app.logger.debug('Webhook signature check ok')
    else:
       app.logger.debug('Webhook signature check failed')

    token = '237a056de90ec7bfaba89af19302e391'
    headers = {
        'Accept': 'Application/json', 'Authorization': 'Bearer ' + token
    };

    if request.method == 'GET':
        app.logger.debug('PING (get)')
        return "OK"

    data = json.loads(json.dumps(request.get_json()))

    if (request.method == 'POST' and (not data.get('url'))):
        app.logger.debug('PING (post)')
        return "OK"

    else:
        url = data["url"]
        event = data["event"] 

        if event == "EXERCISE":
          url = url + '?samples=true&zones=true'

        r = requests.get(url, headers=headers)

        app.logger.debug('WEBHOOK: ' + json.dumps(request.get_json()))
        app.logger.debug('url: ' + url)
        app.logger.debug('event: ' + event)

        if event == "EXERCISE" or event == "SLEEP_WISE_CIRCADIAN_BEDTIME" or event == "SLEEP_WISE_ALERTNESS":
          if "entity_id" in data: 
              entity_id = data['entity_id']
          else:
              entity_id = ""
          timestamp = data['timestamp']
          app.logger.debug('entity id ' + entity_id)
          filename = event+"."+timestamp+"."+entity_id+".json"
          app.logger.debug('writing file ' + filename)
          with open(filename, "w") as outfile:
            json.dump(r.json(), outfile)
        else:
          date = data['date']
          filename = event+"."+date+".json"
          app.logger.debug('writing file ' + filename)
          with open(filename, "w") as outfile:
            json.dump(r.json(), outfile)

    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
