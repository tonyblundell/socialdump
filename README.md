socialdump
==========

Pulls data from a list of RSS feeds, displays on a home-page.

Runs on Flask and MongoDB.

See http://tonyblundell.net for an example.

Run 'python socialdump.py pull' to parse latest feeds via RSS.

See inline comments in socialdump.py and models.py for more info.


Dependencies
------------

Flask 0.9
Feedparser 5.1.2
Mongoengine fork at https://github.com/tonyblundell/mongoengine