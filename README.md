socialdump
==========

Pulls data from a list of RSS feeds, displays on a home-page.

Runs on Flask and MongoDB.

Dependencies: flask, pymongo, feedparser.

config.py is where the list of feeds is kept (along with some other settings), comments and an example are included.

feedme.py parses the feeds and should be run regularly as a cron-job or similar.

socialdump.py is the Flask server that serves the page.
