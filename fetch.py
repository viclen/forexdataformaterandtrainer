from urllib.request import urlopen
import time
import json

jsonurl = "http://data.fixer.io/api/latest?access_key=ef70ac307fa622227ac13b8fc9e74610&symbols=USD,AUD,CAD,PLN,MXN&format=1"

while True:
    f = open('lastest_rates.json','r')
    oldData = f.read()
    f.close()
    response = urlopen(jsonurl)
    json = response.read().decode("utf-8")
    f = open('lastest_rates.json','w+')
    f.write("{}{},".format(oldData, json))
    f.close()
    print("Written!")
    time.sleep(3600)