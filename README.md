Event Syncer
===
# Introduction

Sync events among google calendar, facebook post/events and other cloud tools
for managing events notification in Taiwan Linux Kernel Hackers group
automatically.

# Usage

1. Get facebook authendication key from graph API website
   `https://developers.facebook.com/tools/explorer/`
   Please remember to enable `uesr_events`, and `user_managed_groups`
   permission.
2. Follow the steps to get google calendar secret file
   https://developers.google.com/google-apps/calendar/quickstart/python

3. Check configs in `event_tools/config.py` and check all the `__TBD__` fields
4. Install required packages
   ```
   $ pip install --upgrade -r requirements.txt
   ```

5. Command to sync events is `event_syncer`, the usage is
   ```
   Usage: event_syncer [-h] [-s SOURCE]

   optional arguments:
     -h, --help            show this help message and exit
     -s SOURCE, --source SOURCE
                           source of events
   ```

Currently source 'facebook', the default value, is the only supported publisher.

Supported subscribers:
* google calendar

# Internals

* The event_tools contains the utilities, i.e. `event_utils.py`.
* The subscribers must be derived from base class `EventSubscriberBase`.

# License

2-clause BSD license

Viller Hsiao (villerhsiao@gmail.com)
