import os
from flask import Flask, render_template, request, redirect
import pymongo
from pymongo import MongoClient

MONGO_HOST = os.environ.get('MONGO_HOST', "mongo")
client = MongoClient(MONGO_HOST)

# Specify the database
db = client.app

if not db.counter.find_one():
    db.counter.insert({'value': 1})

app = Flask(__name__)
app.debug = True

@app.route("/", methods=['GET'])
def index():
    counter_val = db.counter.find_one()['value']
    return render_template('index.html', counter_val=counter_val)

@app.route("/", methods=['POST'])
def increment():
    counter_obj = db.counter.find_one()
    db.counter.update({
      '_id': counter_obj['_id']
    },{
      '$inc': {
        'value': 1
      }
    }, upsert=False, multi=False)
    counter_val = db.counter.find_one()['value']
    return render_template('index.html', counter_val=counter_val)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)



