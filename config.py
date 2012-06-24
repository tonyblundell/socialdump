DEBUG = False

TIME_OFFSET = 6 # In hours. Use to normalize the 'posted * hours ago' times.

MONGO_PORT = 23619

DB = 'socialdump'

TITLE = "My Title"

TAG_LINE = "My Tagline"

CONTACT = ('mailto:example@example.com', 'example@example.com')

NUM_COLS = 3

FEEDS = (
	{
		'label':						'myfeed',
		'pretty_label': 				'My Feed',
		'feed_url':						'http://example.com/feed.rss',
		'home_url':						'http://example.com',
		'num_posts':					5,
		'entire_post_is_a_link':		False,
		'string_to_filter_from_posts':	'',
	},
)