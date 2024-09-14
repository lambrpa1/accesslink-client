from flask import Flask, render_template, request, json, jsonify, send_from_directory
from pathlib import Path

import os
import logging, requests
import hmac, hashlib, base64


certfile = os.environ.get('CERTFILE')
certkey = os.environ.get('CERTKEY')
API_SECRET_KEY = os.environ.get('POLAR_API_SECRET_KEY')
token=os.environ.get('POLAR_ACCESS_TOKEN')


print("Cert file            : " + certfile)
print("Cert key             : " + certkey)
print("Access token         : " + token)
print("Polar API secret key : " + API_SECRET_KEY) 

app = Flask(__name__)

def verify_webhook(data, hmac_header):
    digest = hmac.new(API_SECRET_KEY.encode('utf-8'), data, digestmod=hashlib.sha256).digest()
    computed_hmac = digest.hex().encode('utf-8')

    return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():

    polarsignature = request.headers.get('Polar-Webhook-Signature')

    if polarsignature is not None:
        app.logger.debug('Signature created by Polar : ' + polarsignature)
        digest = hmac.new(API_SECRET_KEY.encode('utf-8'), request.get_data(), digestmod=hashlib.sha256).digest()
        app.logger.debug('Calculated signature       : ' + digest.hex())

        verified = verify_webhook(request.get_data(), request.headers.get('Polar-Webhook-Signature'))

        if verified:
            app.logger.debug('Webhook signature check ok')
        else:
            app.logger.debug('Webhook signature check failed')

    headers = {
        'Accept': 'Application/json', 'Authorization': 'Bearer ' + token
    };

    if request.method == 'GET':
        app.logger.info('PING (get)')
        data = { 
            "status" : "OK" 
        } 
        return jsonify(data) 

    data = json.loads(json.dumps(request.get_json()))

    if (request.method == 'POST' and (not data.get('url'))):
        app.logger.info('PING (post)')
        data = {
            "status" : "OK"
        }
        return jsonify(data)
    else:
        url = data["url"]
        event = data["event"] 

        if event == "EXERCISE":
          url = url + '?samples=true&zones=true&route=true'

        r = requests.get(url, headers=headers)

        app.logger.debug('WEBHOOK: ' + json.dumps(request.get_json()))
        app.logger.debug('url: ' + url)
        app.logger.debug('event: ' + event)

        if event == "EXERCISE" or event == "SLEEP_WISE_CIRCADIAN_BEDTIME" or event == "SLEEP_WISE_ALERTNESS":
          if event == "EXERCISE":
              exer=r.json()
              sport=exer['detailed_sport_info']
              filename = 'data/TEMP/'+event+"."+data['timestamp']+"."+sport+".json"
          else:
              filename = 'data/TEMP/'+event+"."+data['timestamp']+".json"
          app.logger.info('writing file ' + filename)
          with open(filename, "w") as outfile:
            json.dump(r.json(), outfile)
        else:
          date = data['date']
          filename = 'data/TEMP/'+event+"."+date+".json"
          app.logger.info('writing file ' + filename)
          with open(filename, "w") as outfile:
            json.dump(r.json(), outfile)

    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8443, debug=True, ssl_context=(certfile, certkey))

