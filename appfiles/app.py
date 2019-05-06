from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")


# Route to render index.html template using data from Mongo
@app.route("/")
def home():
    marsinfo = mongo.db.listings.find_one()
    if marsinfo==None:
        return redirect("/scrape")
    else:
        return render_template("index.html", marsinfo = marsinfo)


# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():

    listings = mongo.db.listings
    listings_data = scrape_mars.scrape()
    listings.update({}, listings_data, upsert=True)
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)
