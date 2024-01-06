import requests, json

token = '237a056de90ec7bfaba89af19302e391'

headers = {
	'Accept': 'Application/json', 'Authorization': 'Bearer ' + token
};

r = requests.get('https://polaraccesslink.com/v3/exercises/yqgj7nLO?samples=true&zones=true', headers=headers);

print (r.status_code)

if r.status_code == 200:
	print (r.json())
	with open("treeni.json", "w") as outfile:
		json.dump(r.json(), outfile)
 
