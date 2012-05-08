from datetime import datetime
import feedparser
from pymongo import Connection
import config
from time import mktime


def main():
    
    # Connect to mongo
    connection = Connection(port=config.MONGO_PORT)
    db = connection[config.DB]

    # Parse each feed in turn 
    for feed in config.FEEDS:

        # Each feed has it's own mongo collection
        coll = db[feed['label']]

        # Parse the feed's URL using the feedparser library
        parsed = feedparser.parse(feed['feed_url'])

        # Add each entry in turn
        for entry in parsed.entries:

            # Pull the required attributes from the entry object
            for attr in ('id', 'date_parsed', 'title', 'link'):
                setattr(entry, attr, getattr(entry, attr, None))

            # Parse the entry's date/time to a datetime object
            entry.date_parsed = datetime.fromtimestamp(mktime(entry.date_parsed)) if entry.date_parsed else None

            # If the entry doesn't have an ID, use it's date/time instead
            entry.id = entry.id or entry.date_parsed

            # Filter any unwanted text from the entrie's title
            entry.title = entry.title.replace(feed['string_to_filter_from_posts'], '') if feed['string_to_filter_from_posts'] else entry.title
            entry.title = entry.title.strip()
            entry.title = entry.title if entry.title.startswith('http') else entry.title[0].upper() + entry.title[1:]

            # If we successfully got an ID, date/time and title from the feed, we can insert into the DB
            if entry.id and entry.date_parsed and entry.title:

                # Check for this feed's ID in the DB, don't insert twice
                if not coll.find_one({'id': entry.id}):

                    # Create a doc for mongo (a python dict will do)
                    doc = {
                        'id': entry.id,
                        'time': entry.date_parsed,
                        'detail': entry.title,
                        'url': entry.link
                    }
                    coll.insert(doc)


if __name__ == '__main__':
    main()