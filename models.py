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
    strp = StringField(default='') # String to strip from start of all posts
    psts = CappedSortedListField(EmbeddedDocumentField(Post), cap=15, ordering='dt', reverse=True)
    meta = {'ordering': ['ordr']}

    def __unicode__(self):
        return self.lbl.encode('utf-8')

    def parse_feedparser_entry(self, entry):
        """
            Parse a feedparser entry object to a post in self.psts (if not already existant).
        """
        uid = getattr(entry, 'id', None) or entry.link
        dt = datetime.datetime(*(entry.published_parsed[:6]))
        txt = entry.title.replace(self.strp, '')
        txt = (txt[0] if txt.startswith('http') else txt[0].upper()) + txt[1:]
        url = entry.link

        # If the post already exists, update it 
        for i, pst in enumerate(self.psts):
            if pst.uid == uid or pst.txt == txt:
                pst.dt = max(pst.dt, dt)
                pst.txt = txt
                pst.url = url
                self.psts[i] = pst
                self.save()
                return

        # Otherwise, just add the post to the list
        pst = Post(uid=uid, dt=dt, txt=txt, url=url)
        self.psts.append(pst)

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
