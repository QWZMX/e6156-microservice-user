from fastapi import FastAPI, Response

# I like to launch directly and not use the standard FastAPI startup
import uvicorn
from flask import Flask,jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route("/", methods=['GET'])
def root():
    return jsonify(message="Hello World")

# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8012)
