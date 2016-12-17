# -*- coding: utf8 -*-

import datetime

from facebook import *

import event_utils
from config import FB_GROUP_ID

class GraphAPIExt(GraphAPI):
    """ Extension of Facebook Graph API library

    Support accessing group event

    """
    def __init__(self, access_token=None, timeout=None, version='2.7',
                 proxies=None):
        super(GraphAPIExt, self).__init__(access_token, timeout, version, proxies)

    def get_group_events(self, group_id, **args):
        """Fetches group"""
        path = '{}/{}/events'.format(self.version, group_id)
        return self.request(path, args)


class FacebookAPI(object):
    """Event publisher: The facebook group events."""

    def __init__(self, token=''):
        self.token = token
        self.graph = GraphAPIExt(access_token=token)

    def _to_event_object(self, fbevent):
        """Transfer downloaded event text into EventObject type."""
        return event_utils.EventObject.setup(
                   title=fbevent['name'],
                   description=fbevent['description'],
                   start_time=event_utils.rfc3339_to_ptime(fbevent['start_time']),
                   end_time=event_utils.rfc3339_to_ptime(fbevent['end_time']),
                   place=fbevent['place']['name'] or '')

    def get_events(self, group_id, start_date=datetime.datetime(2000, 1, 1),
                         end_date=datetime.datetime(2100, 1, 1)):
        """Get group events. Return list of EventObject."""

        fields = 'name,description,place,start_time,end_time'
        start_epoch = event_utils.ptime_to_epoch(start_date)
        events = self.graph.get_group_events(group_id,
                                             fields=fields,
                                             since=start_epoch)

        ret = [self._to_event_object(evt) for evt in events['data']]
        return ret

"""Module test."""
def _print_content(evt):
    print u'    title: {}'.format(evt.get_title())
    print u'    place: {}'.format(evt.get_place())
    print u'    start_time: {}'.format(evt.get_start_time())
    print u'    end_time: {}'.format(evt.get_end_time())
    print u'    description: {}'.format(evt.get_description())

def _test_facebook_api():
    # get the token from graph api explorer first
    token='#'
    fb = FacebookAPI(token)
    evts = fb.get_events(group_id=FB_GROUP_ID,
                         start_date=datetime.datetime(2016,11,5))
    map(lambda e: _print_content(e), evts)

if __name__ == '__main__':
    _test_facebook_api()
