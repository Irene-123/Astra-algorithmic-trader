from flask import Flask

app = Flask(__name__)

@app.route('/api/fetch_portfolio', methods=["GET"])
def fetch_portfolio():
    pass