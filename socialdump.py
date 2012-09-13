import cgi
import config
from datetime import datetime
from datetime import timedelta
from flask import Flask, render_template
import pymongo
import re
import sys
import mongoengine
from models import Feed

app = Flask(__name__)


@app.route('/')
def index():
    """
        The index page of our site. Grabs feeds from Mongo, renders with a Jinja template.
    """

    mongoengine.connect('socialdump')
    return render_template('index.html', feeds=Feed.objects)


@app.template_filter()
def twitterize(s):
    """
        Jinja filter replaces twitter usernames and hashtags with anchor tags
    """
    #s = cgi.escape(s)
    s = re.sub(r'(\s+|\A)@([a-zA-Z0-9\-_]*)\b',r'\1<a href="http://twitter.com/\2">@\2</a>', s)
    s = re.sub(r'(\s+|\A)#([a-zA-Z0-9\-_]*)\b',r'\1<a href="http://search.twitter.com/search?q=%23\2">#\2</a>', s)
    return s


@app.template_filter()
def time_since(dt, default='just now'):
    """
        Jinja filter replaces a date-time with an age string ('3 hours ago', '2 days ago', etc.)
    """
    now = datetime.now() + timedelta(hours=config.TIME_OFFSET)
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


if __name__ == '__main__':
    try:
        config_module = sys.argv[1]
    except IndexError:
        config_module = 'config'
    config = __import__(config_module)
    app.run(host=config.HOST, debug=config.DEBUG);
