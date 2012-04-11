from datetime import datetime
import feedparser
from pymongo import Connection
import config
from time import mktime


def main():
    
    connection = Connection(port=config.MONGO_PORT)
    db = connection[config.DB]

    for feed in config.FEEDS:
        coll = db[feed['label']]
        parsed = feedparser.parse(feed['feed_url'])

        for entry in parsed.entries:

            for attr in ('id', 'date_parsed', 'title', 'link'):
                setattr(entry, attr, getattr(entry, attr, None))

            entry.date_parsed = datetime.fromtimestamp(mktime(entry.date_parsed)) if entry.date_parsed else None
            entry.id = entry.id or entry.date_parsed
            entry.title = entry.title.replace(feed['string_to_filter_from_posts'], '') if feed['string_to_filter_from_posts'] else entry.title

            if entry.id and entry.date_parsed and entry.title:
                if not coll.find_one({'id': entry.id}):
                    last = coll.find().sort('time', -1).limit(1)
                    if last:
                        last = last[0]
                        if last['detail'] == entry.title:
                            coll.update(last, {'time': entry.date_parsed})
                        else:
                            coll.insert({
                                'id': entry.id,
                                'time': entry.date_parsed,
                                'detail': entry.title,
                                'url': entry.link
                            })


if __name__ == '__main__':
    main()
