from flask import Flask
from pymongo import MongoClient
import os

app = Flask(__name__)

def get_database():
    if ("db_root_password" in os.environ):
        client = MongoClient(
            host=os.environ["MY_RELEASE_MONGODB_SERVICE_HOST"] + ":" + os.environ["MY_RELEASE_MONGODB_SERVICE_PORT"],
            username="root",
            password=os.environ["db_root_password"]
        )
    else:
        client = MongoClient(
            host=os.environ["MY_RELEASE_MONGODB_SERVICE_HOST"] + ":" + os.environ["MY_RELEASE_MONGODB_SERVICE_PORT"]
        )

    return client[os.environ["db_name"]]

@app.route("/")
def index():
    try:
        db = get_database()
        users = db["users"].find()
        count = 0
        for user in users:
            count += 1
        return "ims-api index page: Connection to mongodb successful. Users: " + str(count)
    except:
        return "ims-api index page: Connection to mongodb failed"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)