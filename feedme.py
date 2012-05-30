from datetime import datetime
import feedparser
import pymongo
import sys
from time import mktime


def main():
    
    # Connect to mongo
    connection = pymongo.Connection(port=config.MONGO_PORT)
    db = connection[config.DB]

    # Parse each feed in turn 
    for feed in config.FEEDS:

        # Each feed has it's own mongo collection
        coll = db[feed['label']]

        # Grab the last entry, we'll use it to ensure we don't enter duplicates
        last_list = coll.find().sort('time', pymongo.DESCENDING).limit(1)
        last = last_list[0] if last_list.count() > 0 else {'detail': None}

        # Parse the feed's URL using the feedparser library
        parsed = feedparser.parse(feed['feed_url'])

        # Add each entry in turn
        for entry in parsed.entries:

            # Parse the entry's date/time to a datetime object
            entry.date_parsed = getattr(entry, 'date_parsed', None)
            entry.date_parsed = datetime.fromtimestamp(mktime(entry.date_parsed)) if entry.date_parsed else datetime.now()

            # If the entry doesn't have an ID, use it's date/time instead
            entry.id = getattr(entry, 'id', entry.date_parsed)

            # Filter any unwanted text from the entrie's title
            entry.title = getattr(entry, 'title', '')
            entry.title = entry.title.replace(feed['string_to_filter_from_posts'], '') if feed['string_to_filter_from_posts'] else entry.title
            entry.title = entry.title.strip()
            entry.title = entry.title if entry.title.startswith('http') else entry.title[0].upper() + entry.title[1:]

            # The entry may have a link, set to None if not, so we can still ref the attr
            entry.link = getattr(entry, 'link', None)

            # If we successfully got an ID, date/time and title from the feed, we can insert into the DB
            if entry.id and entry.date_parsed and entry.title:

                # Check for this feed's ID in the DB, don't insert twice
                if not coll.find_one({'id': entry.id}) and not last['detail'] == entry.title:

                    # Create a doc for mongo (a python dict will do)
                    doc = {
                        'id': entry.id,
                        'time': entry.date_parsed,
                        'detail': entry.title,
                        'url': entry.link
                    }
                    coll.insert(doc)

                    # The newly inserted item will be used for comparison next time
                    last == doc


if __name__ == '__main__':
    try:
        config_module = sys.argv[1]
    except IndexError:
        config_module = 'config'
    config = __import__(config_module)
    main()