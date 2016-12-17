# -*- coding: utf-8 -*-
import re
from collections import defaultdict
from datetime import datetime

from rfc3339 import rfc3339
from dateutil import parser as dparser

from config import VIDEO_CONF_URL

def ptime_to_epoch(ptime=datetime(1970,1,1)):
    """Transfer from python datetime to epoch time format."""
    return int((ptime - datetime(1970,1,1)).total_seconds())

def ptime_to_rfc3339(ptime=datetime.now()):
    """Transfer from python datetime to RFC3339 time string, which is widely
       used by cloud service like google or facebook.
    """
    return rfc3339(ptime)

def rfc3339_to_ptime(rfctime='2016-01-01T00:00:00+08:00'):
    """Transfer from RFC3339 time string to python datetime."""
    return dparser.parse(rfctime)

class EventObject(object):
    """Class to encapsulate an group activity event

    Unify the event interface among different cloud publisher and subscribers,
    facebook event, google calendar and so on.

    It classify the event into difference attributes, i.e. event type, title,
    subtitle, ... etc. There is a classmethod setup() to setup the event by
    parsing a preformatted text.

    Some utililties to get necessary information about the event are listed
    below,
        get_title
        get_place
        get_start_time
        get_end_time
        get_description
    """

    def __init__(self,
                 etype=u'主題分享', etitle=u'', esubtitle=u'', epresenter=u'',
                 estart=datetime.now(), eend=datetime.now(),
                 edocurl=u'', einfo=u'', eplace=VIDEO_CONF_URL):
        """Fill the event information

        Args:
           etype - event type, e.g. '讀書會', '主題分享' ... etc
           etitle - title string
           esubtitle - sub title string, like chapter title in a book
           epresenter - presenter string
           estart - python datetime object of event starting time
           eend - python datetime object of event ending time
           edocurl - URL of the note document
           einfo - detail description about the event
           eplace - where the event is hold

        """
        self.type = etype.strip()
        self.title = etitle.strip()
        self.subtitle = esubtitle.strip()
        self.presenter = epresenter.strip()
        self.start_time = estart
        self.end_time = eend
        self.doc_url = edocurl.strip()
        self.info = einfo.strip()
        self.place = eplace.strip()

    @staticmethod
    def parse_title(title=''):
        """Parse a formatted string title to dictionary."""
        data = filter(bool, re.split(u':|：', title, 1))
        if title == '':
            return {}
        elif len(data) == 2:
            return {'etype': data[0], 'etitle': data[1]}
        elif len(data) == 1:
            return {'etitle': data[0]}
        else:
            return {'etitle': data[0]}

    @staticmethod
    def parse_description(description=''):
        """Parse string format description to dictionary."""
        key = ''
        val = ''
        ret = {}
        for desc in description.splitlines():
            desc = desc.strip().replace(u'：', u':', 1)
            if u'內容:' in desc:
                key = 'esubtitle'
                val = desc.replace(u'內容:', '', 1)
            elif u'主講:' in desc:
                key = 'epresenter'
                val = desc.replace(u'主講:', '', 1)
            elif u'筆記:' in desc:
                key = 'edocurl'
                val = desc.replace(u'筆記:', '', 1)
            elif u'其他資訊:' in desc:
                key = 'einfo'
                val = desc.replace(u'其他資訊:', '', 1)
            elif u'時間:' in desc or  u'地點:' in desc:
                key = ''
            else:
                val = desc

            val = ret.get(key, '') + val + '\n'
            if key:
                ret.update({key: val})

        return ret

    @classmethod
    def setup(cls, title='', description='', start_time=datetime.now(),
                   end_time=datetime(2100, 1, 1), place=''):
        """The text format is
            TITLE FORMAT =>
                'title type' : 'title string'

            DESCRIPTION FORMAT =>
                '內容': 'subtitle'
                '主講': 'presenter'
                '筆記': 'document url'
                '其他資訊': 'detail or other description'
                '時間': 'presentation time, same as start_time and end time'
                '地點': 'presentation place, same as place args'

                '時間' and '地點' are duplicate information and will be ignored.
        """
        args = dict()
        args.update(cls.parse_title(title))
        args.update(cls.parse_description(description))
        args.update(dict(estart=start_time))
        args.update(dict(eend=end_time))
        args.update(dict(eplace=place) if not place else {})
        return cls(**args)

    def _format_time(self, time, fmt):
        """Return time with specific format."""
        if fmt == 'ptime':
            return time
        elif fmt == 'rfc3339':
            return ptime_to_rfc3339(time)

    def get_title(self):
        """Return the title string."""
        return u'[{}] {}'.format(self.type, self.title)

    def get_place(self):
        """Return the event place string."""
        return self.place

    def get_start_time(self, fmt='ptime'):
        """Return the event starting time string with different format.

        Args:
            fmt - supported formats are
                  'ptime' for python datetime format
                  'rfc3339' for rfc3339 format
        """
        return self._format_time(self.start_time, fmt)

    def get_end_time(self, fmt='ptime'):
        """Return the event ending time string with different format.

        Args:
            fmt - supported formats are
                  'ptime' for python datetime format
                  'rfc3339' for rfc3339 format
        """
        return self._format_time(self.end_time, fmt)

    def get_description(self):
        """Return all other information."""
        desc = u''
        desc = desc + (u'內容: {}\n'.format(self.subtitle)
                          if self.subtitle else u'')
        desc = desc + (u'主講: {}\n'.format(self.presenter)
                          if self.presenter else u'')
        desc = desc + u'時間: {} ~ {}\n'.format(
                        self.start_time.strftime('%Y-%m-%d %H:%M'),
                        self.end_time.strftime('%H:%M'))
        desc = desc + (u'地點: {}\n'.format(self.place)
                          if self.place else u'')
        desc = desc + (u'筆記: {}\n'.format(self.doc_url)
                          if self.doc_url else u'')
        desc = desc + (u'其他資訊: {}\n'.format(self.info)
                          if self.info else u'')
        return desc

class EventGateway(object):
    """Implements gateway for event publisher and subscriber."""

    def __init__(self):
        self._subscribers = set()

    def register(self, subscriber):
        self._subscribers.add(subscriber)

    def unregister(self, subscriber):
        self._subscribers.remove(subscriber)

    def update_event(self, event):
        for subr in self._subscribers:
            subr.update_event(event)

_evt_gateways = defaultdict(EventGateway)

def get_event_gateway(name):
    return _evt_gateways[name]

class EventSubscriberBase(object):
    """Base class for event subscribers."""
    def __init__(self, gateway_name='none'):
        self.event_gateway = get_event_gateway(gateway_name)
        self.event_gateway.register(self)

    def get_auth(self):
        pass

    def update_event(self, event):
        pass

""" module test functions."""
def _test_time_utils():
    print 'Test time utilities =>'
    print '    Show epoch time: {}'.format(ptime_to_epoch(datetime.now()))
    print '    Show rfc3339 time: {}'.format(ptime_to_rfc3339())
    print '    Show python datetime: {}'.format(rfc3339_to_ptime())

def _test_evtobj_init():
    print '\nTest EventObject constructor =>'
    evt = EventObject(etype=u'讀書會',
                      etitle=u'Linux 環境編程:從應用到內核 第六章',
                      esubtitle=u'第六章 信號',
                      epresenter=u'Someone',
                      estart=datetime(2016, 12, 13, 20, 0),
                      eend=datetime(2016, 12, 13, 22, 0),
                      edocurl=u'https://docs.google.com/document/d/1KggWdjGOQd5oV-wCW4MGttLemvP0U0CDuzYmN4SLtns',
                      einfo=u'https://hackmd.io/s/rJVila1o#第6章',
                      eplace=VIDEO_CONF_URL)


    print u'    title: {}'.format(evt.get_title())
    print u'    place: {}'.format(evt.get_place())
    print u'    start_time: {}'.format(evt.get_start_time())
    print u'    end_time: {}'.format(evt.get_end_time())
    print u'    description: {}'.format(evt.get_description())

def _test_evtobj_setup():
    print '\nTest EventObject setup() class method =>'
    evt = EventObject.setup(title=u'讀書會：Linux 環境編程-從應用到內核 第六章',
                      start_time=datetime(2016, 12, 13, 20, 0),
                      end_time=datetime(2016, 12, 13, 22, 0),
                      place=VIDEO_CONF_URL,
                      description=u"""內容: 第六章 信號
主講: Someone/Otherone

時間： 2016-12-13 20:00 ~ 22:00

地點: http://zoom.us/j/2109998888
筆記: https://docs.google.com/document/d/1KggWdjGOQd5oV-wCW4MGttLemvP0U0CDuzYmN4SLtns
其他資訊： 請自行前往下面網址查看

https://hackmd.io/s/rJVila1o#第6章
未滿三行劣退""")

    print u'    title: {}'.format(evt.get_title())
    print u'    place: {}'.format(evt.get_place())
    print u'    start_time: {}'.format(evt.get_start_time())
    print u'    end_time: {}'.format(evt.get_end_time())
    print u'    description: {}'.format(evt.get_description())


if __name__ == '__main__':
    _test_time_utils()
    _test_evtobj_init()
    _test_evtobj_setup()
