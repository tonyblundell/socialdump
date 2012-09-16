import datetime
import feedparser
from mongoengine import *


class Post(EmbeddedDocument):
    uid = StringField(required=True)
    txt = StringField(required=True)
    dt = DateTimeField(required=True)
    url = URLField()

    def __unicode__(self):
        return self.txt.encode('utf-8')[:10]


class Feed(Document):
    ordr = IntField(default=0)
    lbl = StringField(required=True, primary_key=True)
    furl = URLField(required=True) # Feed URL
    surl = URLField() # Site URL
    lnk = BooleanField(default=False) # Entire post is a link
    strp = StringField(default='') # String to strip from post text
    psts = CappedSortedListField(EmbeddedDocumentField(Post), cap=15, ordering='dt', reverse=True)
    meta = {'ordering': ['ordr']}

    def __unicode__(self):
        return self.lbl.encode('utf-8')

    def parse_feedparser_entry(self, entry):
        """
            Parses a feedparser entry object to a post in self.psts (if not already existant).
        """
        uid = getattr(entry, 'id', None) or entry.link
        for post in self.psts:
            if post.uid == uid:
                return
        post = Post()
        post.uid = uid
        post.txt = entry.title.replace(self.strp, '')
        post.txt = (post.txt[0] if post.txt.startswith('http') else post.txt[0].upper()) + post.txt[1:]
        post.dt = datetime.datetime(*(entry.published_parsed[:6]))
        post.url = entry.link
        self.psts.append(post)

    def pull(self):
        """
            Download the RSS/ATOM feed, parse with feedparser, add new posts.
        """
        for entry in feedparser.parse(self.furl).entries:
            try:
                self.parse_feedparser_entry(entry)
            except AttributeError:
                pass # Couldn't add entry as it was incomplete
        self.save()


if __name__ == '__main__':
    for feed in Feed.objects:
        feed.pull()