import cgi
import config
from datetime import datetime
from datetime import timedelta
from flask import Flask, render_template
import pymongo
import re


app = Flask(__name__)


@app.route('/')
def index():
    """
        The index page of our site. Grabs feeds from Mongo, renders with a Jinja template.
    """

    # Connect to mongo
    connection = pymongo.Connection(port=config.MONGO_PORT)
    db = connection[config.DB]

    # Grab our feeds
    feeds = []
    for feed in config.FEEDS:
        posts = db[feed['label']].find().sort('time', pymongo.DESCENDING).limit(feed['num_posts'])
        feeds.append((feed['pretty_label'], feed['home_url'], feed['entire_post_is_a_link'], posts))

    # Build some data to send to the template
    kwargs = {
        'title': config.TITLE,
        'tag_line': config.TAG_LINE,
        'num_cols': config.NUM_COLS,
        'contact': config.CONTACT,
        'feeds': feeds
    }

    return render_template('index.html', **kwargs)


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
    app.run(debug=config.DEBUG);
