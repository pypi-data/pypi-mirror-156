from flask import Flask, request, jsonify

tags = {}

app = Flask(__name__)

@app.route("/opc/update_tags", methods=["POST"])

def update_tags():
    response = request.json
    for tag in response.keys():
        tags[tag]={
            "value":response[tag]["value"],
            "timestamp":response[tag]["timestamp"],
            "quality":response[tag]["quality"]}
    return jsonify(tags)

@app.route("/opc/get_tags", methods=["GET"])
def get_tags():
    return jsonify(tags)

if __name__ == '__main__':
    app.run(debug=True)