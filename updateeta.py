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
        sendObj = {}
        try:
            db = connect_to_cloudsql()
            cursor = db.cursor()
            cursor2 = db.cursor()
            cursor3 = db.cursor()
            cursor.execute('use meetup_db')
            cursor2.execute('use meetup_db')
            cursor3.execute('use meetup_db')
            userid = self.request.get('userid')
            eta = self.request.get('eta')
            historyid = int(self.request.get('historyid'))

            query = "select * from history where historyid = %d"%(historyid)
            cursor.execute(query)
            arrayeta = []

            usereta = []
            invited = []
            for r in cursor.fetchall():
                etaobj = {}
                invited = []
                usereta = []
                createdby = r[8]
                invited = r[2].split('|')
                usereta = r[12].split('|')
                if createdby == userid:
                    uindex = len(usereta) - 1
                else:
                    uindex = invited.index(userid)
                usereta[uindex] = eta
                eventQuery = "update history set usereta = '%s' where historyid = %d "%("|".join(usereta),historyid)
                cursor2.execute(eventQuery)
                invited.append(createdby)
                for uid in invited:
                    person = {}
                    getUsername = "select username from users where userid = '%s'"%(uid)
                    cursor3.execute(getUsername)
                    allUsers = cursor3.fetchall()
                    #etaobj[uid] = allUsers[0][0]
                    person['name'] = allUsers[0][0]
                    person['eta'] = usereta[invited.index(uid)]
                    arrayeta.append(person)

            #obj['usereta'] = etaobj
            db.commit()
            sendObj['usereta'] = arrayeta
            sendObj['status'] = "success"
        except Exception as e:
            self.response.out.write(e)

        self.response.out.write(json.dumps(sendObj))

app = webapp2.WSGIApplication([
    ('/updateeta', MainPage),
], debug=True)

# [END all]
