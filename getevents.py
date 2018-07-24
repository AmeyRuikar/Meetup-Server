# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Sample App Engine application demonstrating how to connect to Google Cloud SQL
using App Engine's native unix socket or using TCP when running locally.

For more information, see the README.md.
"""

# [START all]
import os

import MySQLdb
import webapp2
import json
import time


# These environment variables are configured in app.yaml.
CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')


def connect_to_cloudsql():
    # When deployed to App Engine, the `SERVER_SOFTWARE` environment variable
    # will be set to 'Google App Engine/version'.
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        # Connect using the unix socket located at
        # /cloudsql/cloudsql-connection-name.
        cloudsql_unix_socket = os.path.join(
            '/cloudsql', CLOUDSQL_CONNECTION_NAME)

        db = MySQLdb.connect(
            unix_socket=cloudsql_unix_socket,
            user=CLOUDSQL_USER,
            passwd=CLOUDSQL_PASSWORD)

    # If the unix socket is unavailable, then try to connect using TCP. This
    # will work if you're running a local MySQL server or using the Cloud SQL
    # proxy, for example:
    #
    #   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
    #
    else:
        db = MySQLdb.connect(
            host='127.0.0.1', user=CLOUDSQL_USER, passwd=CLOUDSQL_PASSWORD)

    return db

class MainPage(webapp2.RequestHandler):
    def get(self):
        """Simple request handler that shows all of the MySQL variables."""
        #self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Content-Type'] = 'application/json'

        db = connect_to_cloudsql()
        cursor = db.cursor()
        cursor2 = db.cursor()
        cursor3 = db.cursor()
        cursor4 = db.cursor()
        cursor.execute('use meetup_db')
        cursor2.execute('use meetup_db')
        cursor3.execute('use meetup_db')
        cursor4.execute('use meetup_db')
        #cursor.execute('select * from markers')

        eventStatus = self.request.get('eventType')
        userid = self.request.get('userid')

        query = "select * from history where eventstatus = '%s'"%(eventStatus)
        cursor.execute(query)

        allEvents = []

        for r in cursor.fetchall():
            invites = []
            invites = r[2].split('|')
            if (userid in invites) or userid==r[8]:
                #process this event
                votes = []
                votes = r[6].split('|')
                obj = {}
                obj['eventstarttime'] = r[10]
                obj['eventendtime'] = r[11]
                eventQuery = "select eventname, starttime, endtime, X(eventlocation),Y(eventlocation) from events where eventid = '%s'"%(r[1])
                cursor2.execute(eventQuery)
                for event in cursor2.fetchall():
                    obj['eventName'] = event[0]
                    obj['eventlocationX'] = event[3]
                    obj['eventlocationY'] = event[4]
                    obj['votes'] = votes
                    getUserName = "select username from users where userid = '%s'"%(r[8])
                    cursor3.execute(getUserName)
                    creator = cursor3.fetchall()
                    obj['createdby'] = creator[0][0]
                    obj['historyid'] = r[0]
                    # add suggestions later
                    # TODO get names of invites
                    invited = []
                    for invitedUser in invites:
                        getName = "select username from users where userid = '%s'"%(invitedUser)
                        cursor4.execute(getName)
                        invitedUsername = cursor4.fetchall()
                        invited.append(invitedUsername[0][0])
                    obj['invited'] = invited
                    allEvents.append(obj)
            else:
                #obj['msg'] = "no events for this user"
                pass
        sendObj = {}
        sendObj['status'] = "success"
        sendObj['retrievedEvents'] = allEvents

        self.response.out.write(json.dumps(sendObj))

app = webapp2.WSGIApplication([
    ('/getevents', MainPage),
], debug=True)

# [END all]
