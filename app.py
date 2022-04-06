import os
import requests
import pandas as pd

from bs4 import BeautifulSoup as bs
from flask import Flask, request, render_template, Response
from flask_cors import cross_origin
from io import BytesIO
from urllib.parse import urlencode
from urllib.request import urlopen as uReq

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
@cross_origin()
def home_page():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        try:
            search_query = request.form.get("content")
            encode_query = urlencode({"q": search_query})
            flipkart_url = "https://www.flipkart.com/search?" + encode_query
            uClient = uReq(flipkart_url)
            flipkart_page = uClient.read()
            uClient.close()

            flipkart_html = bs(flipkart_page, "html.parser")
            bigboxes = flipkart_html.find_all("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[:2]

            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})
            
            reviews = []
            for commentbox in commentboxes:
                try:
                    customer_name = commentbox.find_all("p", {"class": "_2sc7ZR _2V5EHH"})[0].text
                except:
                    customer_name = "No Name"

                try:
                    product_rating = commentbox.find_all("div", {"class": "_3LWZlK _1BLPMq"})[0].text
                except:
                    product_rating = "No Rating"

                try:
                    comment_header = commentbox.find_all("p", {"class": "_2-N8zT"})[0].text
                except:
                    comment_header = "No Header"

                try:
                    comment = commentbox.find_all("div", {"class": ""})
                    comment = comment[0].div.text
                except:
                    comment = "No Comment"

                reviews.append({
                    "product_name": search_query,
                    "customer_name": customer_name,
                    "product_rating": product_rating,
                    "comment_header": comment_header,
                    "comment": comment,
                })

            return render_template("index.html", search_query=search_query, reviews=reviews)
        except Exception as e:
            print("The Exception message is: ", e)
            return "Something went wrong!"

@app.route("/download/<search_query>", methods=["GET"])
@cross_origin()
def download_review(search_query):
    encode_query = urlencode({"q": search_query})
    flipkart_url = "https://www.flipkart.com/search?" + encode_query
    uClient = uReq(flipkart_url)
    flipkart_page = uClient.read()
    uClient.close()

    flipkart_html = bs(flipkart_page, "html.parser")
    bigboxes = flipkart_html.find_all("div", {"class": "_1AtVbE col-12-12"})
    del bigboxes[:2]

    box = bigboxes[0]
    productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
    prodRes = requests.get(productLink)
    prodRes.encoding = 'utf-8'
    prod_html = bs(prodRes.text, "html.parser")
    commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})
    
    reviews = []
    for commentbox in commentboxes:
        try:
            customer_name = commentbox.find_all("p", {"class": "_2sc7ZR _2V5EHH"})[0].text
        except:
            customer_name = "No Name"

        try:
            product_rating = commentbox.find_all("div", {"class": "_3LWZlK _1BLPMq"})[0].text
        except:
            product_rating = "No Rating"

        try:
            comment_header = commentbox.find_all("p", {"class": "_2-N8zT"})[0].text
        except:
            comment_header = "No Header"

        try:
            comment = commentbox.find_all("div", {"class": ""})
            comment = comment[0].div.text
        except:
            comment = "No Comment"

        reviews.append({
            "product_name": search_query,
            "customer_name": customer_name,
            "product_rating": product_rating,
            "comment_header": comment_header,
            "comment": comment,
        })

    df = pd.DataFrame(reviews)
    buffer = BytesIO()
    df.to_csv(buffer)
    return Response(buffer.getvalue(),
                    mimetype='text/csv',
                    headers={'Content-Disposition': f'attachment;filename={search_query}.csv'})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
