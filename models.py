import datetime
import feedparser
from mongoengine import *


connect('socialdump')


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
    strp = StringField(default='') # String to strip from start of all posts
    psts = CappedSortedListField(EmbeddedDocumentField(Post), cap=5, ordering='dt', reverse=True)
    meta = {'ordering': ['ordr']}

    def __unicode__(self):
        return self.lbl.encode('utf-8')

    def parse_feedparser_entry(self, entry):
        uid = getattr(entry, 'id', None) or entry.link
        for post in self.psts:
            if post.uid == uid:
                return
        post = Post()
        post.uid = uid
        post.txt = entry.title.replace(self.strp, '').capitalize()
        post.dt = datetime.datetime(*(entry.published_parsed[:6]))
        post.url = entry.link
        self.psts.append(post)

    def pull(self):
        for entry in feedparser.parse(self.furl).entries:
            self.parse_feedparser_entry(entry)
        self.save()
        self.reload()


if __name__ == '__main__':
    for feed in Feed.objects:
        feed.pull()