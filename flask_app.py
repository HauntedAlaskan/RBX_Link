from flask import Flask, request, jsonify

app = Flask(__name__)

keys = {}


@app.route('/verifykey', methods=['POST'])
def verify_key():
    data = request.get_json()
    key = data['key']
    user_id = data['user_id']

    if key in keys and keys[key] == user_id:
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'failure'})


@app.route('/getkey', methods=['GET'])
def get_key():
    key = request.args.get('key')
    if key in keys:
        return jsonify({'status': 'success', 'user_id': keys[key]})
    else:
        return jsonify({'status': 'failure'})


def run_flask_app():
    app.run(debug=True, port=int(os.environ.get('PORT', 5000)))


run_flask_app()
