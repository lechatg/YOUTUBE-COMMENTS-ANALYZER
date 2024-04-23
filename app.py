from flask import Flask, render_template, request, session
import pandas as pd
from flask_session import Session
import redis
import json
import time
import os

# memory_thread - for monitoring ram usage every 10 sec. (to use - enough to activate this import)
# from ram_monitor import memory_thread

from parse_yt_comments import youtube_parse_comments, youtube_parse_name
from cluster import cluster_comments


app = Flask(__name__)

# CONFIGURE SESSION
# Check if REDIS_URL environment variable is set
if "REDIS_URL" in os.environ:
    # Use Redis for session storage
    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_REDIS"] = redis.from_url(os.environ["REDIS_URL"])
else:
    # Fall back to filesystem for session storage
    app.config["SESSION_TYPE"] = "filesystem"

# Set the secret key for session management
app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key")

# Initialize session
Session(app)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        link=request.form.get("given_link")
        start_time = time.time()
        if not check_if_looks_like_youtube_link(link):
            return render_template("index.html", check_failed = 410)

        # Check if link is valid and get video name
        video_name = youtube_parse_name(link)

        if video_name == False:
            return render_template("index.html", check_failed = 420)
        
        print(f'Video link is valid, video name: {video_name}')

        # get video_id (for result.html)
        video_id = link.split('v=')[1]

        print(f'Start parsing comments for {video_name}')

        comments_df = youtube_parse_comments(link)

        print(f'Comments for {video_name} stored in df')

        number_of_comments = len(comments_df)
        
        # get top 10 comments by number of likes
        data_sorted_10 = comments_df.sort_values(by=['likes'], ascending=False).head(10)

        # cluster comments; get main figure, topics table and bar_chart
        figure_and_topics = cluster_comments(comments_df, video_name)
        figure = figure_and_topics[0]
        topics_table = figure_and_topics[1]
        bar_chart = figure_and_topics[2]

        user_dict = { 
            'link': link, 
            'entries': data_sorted_10,
            'fig': figure,
            'comments_number': number_of_comments, 
            'video_name': video_name, 
            'video_id': video_id, 
            'topics_table': topics_table,
            'bar_chart': bar_chart
        }

        # Store generated result in user's session, so that it can be accessed on result page multiple times
        session['user_dict'] = user_dict
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"\nExecution time for {video_name}: {execution_time} seconds")
        return render_template("result.html", user_dict=session['user_dict'])
    
    # If we want to clear result page any time user goes to Search page
    # session['user_dict'] = None

    return render_template("index.html")
    
@app.route("/lastresult", methods=["GET"])
def result_func():
    try:
        user_dict=session['user_dict']
        return render_template("result.html", user_dict=user_dict)
    except KeyError:
        return render_template("noresult.html")

# Check if given link looks like Youtube link
def check_if_looks_like_youtube_link(url):
    if url.startswith("http://") or url.startswith("https://"):
        # Check if the URL contains "youtube.com/watch?v=" or "youtu.be/"
        if "youtube.com/watch?v=" in url or "youtu.be/" in url:
            return True
    return False

@app.route("/howtouse", methods=["GET"])
def howtouse_func():
    with open("static/txtfiles/bar_chart_new_usa_eu.txt", 'r') as txt_file:
        bar_chart = txt_file.read()

    with open("static/txtfiles/fig_new_usa_eu.txt", 'r') as txt_file:
        fig = txt_file.read()
    
    with open('static/jsonfiles/faq.json', 'r') as json_file:
        faq = json.load(json_file)

    return render_template("howtouse.html", bar_chart=bar_chart,fig=fig, faq=faq)
