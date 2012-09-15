import cgi
import datetime
from flask import Flask, render_template
from models import Feed
import mongoengine
import re
import sys

app = Flask(__name__)
app.config.from_object('config')


@app.template_filter()
def twitterize(s):
    """
        Jinja filter replaces twitter usernames and hashtags with anchor tags
    """
    s = re.sub(r'(\s+|\A)@([a-zA-Z0-9\-_]*)\b',r'\1<a href="http://twitter.com/\2">@\2</a>', s)
    s = re.sub(r'(\s+|\A)#([a-zA-Z0-9\-_]*)\b',r'\1<a href="http://search.twitter.com/search?q=%23\2">#\2</a>', s)
    return s


@app.template_filter()
def time_since(dt, default='just now'):
    """
        Jinja filter replaces a date-time with an age string ('3 hours ago', '2 days ago', etc.)
    """
    now = datetime.datetime.utcnow()
    diff = now - dt
    if diff.total_seconds() > 0:
        periods = (
            (diff.days / 365, "year", "years"),
            (diff.days / 30, "month", "months"),
            (diff.days / 7, "week", "weeks"),
            (diff.days, "day", "days"),
            (diff.seconds / 3600, "hour", "hours"),
            (diff.seconds / 60, "minute", "minutes"),
            (diff.seconds, "second", "seconds"),
        )
        for period, singular, plural in periods:
            if period > 0:
                return "%d %s ago" % (period, singular if period == 1 else plural)
    return default


@app.route('/')
def index():
    """
        The index page of our site. Grabs feeds from Mongo, renders with a Jinja template.
    """
    return render_template('index.html', feeds=Feed.objects)


if __name__ == '__main__':
    mongoengine.connect(app.config['MONGODB_DB'])
    if 'pull' in sys.argv:
        for feed in Feed.objects:
            feed.pull()
    else:
        app.run(host=app.config['HOST']);