# -*- coding: utf-8 -*-

import argparse
import httplib2
import logging
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from rfc3339 import rfc3339

from config import *
from event_utils import *

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

class GoogleCalendar(EventSubscriberBase):
    """Event subscriber: google calendar"""

    def __init__(self, event_gateway='none',
                       calendar_id='primary',
                       dir_credential='~/.credentials',
                       attendees=[]):
        super(GoogleCalendar, self).__init__(event_gateway)
        self.dir_credential = dir_credential
        self.calendar_id = calendar_id
        self.attendees = [dict(email=att) for att in attendees]

        parser = argparse.ArgumentParser(parents=[tools.argparser])
        parser.set_defaults(noauth_local_webserver=True)
        self.flags = parser.parse_args()

        logging.basicConfig(filename='/dev/null',level=logging.DEBUG)

    def _get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        dir_credential = os.path.abspath(
                             os.path.expanduser(self.dir_credential))
        if not os.path.exists(dir_credential):
            os.makedirs(dir_credential)
        credential_path = os.path.join(dir_credential,
                                       'google-calendar-secret.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            fsecret = os.path.join(self.dir_credential, CLIENT_SECRET_FILE)
            flow = client.flow_from_clientsecrets(fsecret, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if self.flags:
                credentials = tools.run_flow(flow, store, self.flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def get_auth(self):
        credentials = self._get_credentials()
        return credentials.authorize(httplib2.Http())

    def build_body(self, event):
        body = {
            'summary': event.get_title(),
            'start': { 'dateTime': event.get_start_time(fmt='rfc3339') },
            'end': { 'dateTime': event.get_end_time(fmt='rfc3339') },
            'location': event.get_place(),
            'attendees': self.attendees,
            'description' : event.get_description()}
        return body

    def update_event(self, event):
        http = self.get_auth()
        service = discovery.build('calendar', 'v3', http=http)
        body = self.build_body(event)
        # TODO: replace insert with update
        eventsResult = service.events().insert(
                           calendarId=self.calendar_id,
                           body=body,
                           sendNotifications=True).execute()

# module test
def _test_update_event():
    cal = GoogleCalendar(attendees=[])
    evt = EventObject(etype=u'讀書會',
                      etitle=u'Linux 環境編程:從應用到內核 第六章',
                      esubtitle=u'第六章 信號',
                      epresenter=u'Someone',
                      estart=datetime(2016, 12, 13, 20, 0),
                      eend=datetime(2016, 12, 13, 22, 0),
                      edocurl=u'https://docs.google.com/document/d/1KggWdjGOQd5oV-wCW4MGttLemvP0U0CDuzYmN4SLtns',
                      einfo=u'https://hackmd.io/s/rJVila1o#第6章',
                      eplace=VIDEO_CONF_URL)

    cal.update_event(evt)

if __name__ == '__main__':
    _test_update_event()
