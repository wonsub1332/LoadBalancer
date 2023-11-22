from flask import Flask, request, json, jsonify

app = Flask(__name__)

@app.route("/test", methods=['POST'])
def test():
    params = request.get_json()
    print("받은 Json 데이터 ", params)

    response = {
        "result": "ok"
    }

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9999)