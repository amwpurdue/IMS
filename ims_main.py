from flask import Flask

from ims_api import productsPage

app = Flask(__name__)
app.register_blueprint(productsPage)


@app.route("/")
def index():
    return "main"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)