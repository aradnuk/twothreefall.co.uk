from django.conf.urls import *
from django.contrib.sitemaps import Sitemap
from django.views.generic.list import ListView

import ldates

from models import USER_REGEX
from models import User, WeeksWithSyntaxErrors

# match usernames
__user_base     = '^user/' + USER_REGEX + '/' 

# match week indexes
__date_matcher  = r'(?P<start>\d+)-(?P<end>\d+)/$'
__year_matcher  = r'(?P<year>\d{4})/$'
__default_dates = { 'start': ldates.idx_beginning, 'end': ldates.idx_last_sunday }

urlpatterns = patterns('lastfmexplorer.views',
    # start
    (r'^$', 'start'),
    (r'^status$', 'status'),

    # updates
    (__user_base + 'update/$', 'update'),
    (r'^poll-update$', 'poll_update_status'),

    # invalid XML
    url(r'^bad-weeks$', ListView.as_view(model=WeeksWithSyntaxErrors), name="bad_weeks"),

    # single week chart
    (__user_base + r'chart/week/(?P<start>\d*)/$', 'user_week_chart'),

    # user chart index
    (__user_base + 'index/$', 'user_data'),
)

# Ajax methods
urlpatterns += patterns('lastfmexplorer.views',
    (r'^api/(?P<user_id>\d+)/artistplays/(?P<artist_id>\d+)$', 'weekly_plays_of_artist'),
)


def __urlsForPattern(urlpatterns, pattern, view):
    """Creates urls for root, years and arbitrary dates"""
    urlpatterns += patterns('lastfmexplorer.views',
        (pattern + '$', view, __default_dates),

        # x ago
        (pattern + r'(?P<monthsAgo>\d)month/$', view),
        (pattern + r'(?P<yearsAgo>\d\d?)year/$', view),

        # Arbitrary selection
        (pattern + r'(?P<start>\d+)-(?P<end>\d+)/$', view),

        # Years
        (pattern + r'(?P<year>\d{4})/$', view),
    )

# plain user overview.
__urlsForPattern(urlpatterns, __user_base, 'overview')

# top artist charts
__urlsForPattern(urlpatterns, __user_base + r'chart/', 'user_chart')


# TODO: Django makes it really awkward to include /lastfmexplorer!
class LastfmExplorerSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.25
    def items(self):
        return User.objects.all()
