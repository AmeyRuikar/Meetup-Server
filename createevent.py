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
        cursor.execute('use meetup_db')
        cursor2.execute('use meetup_db')
        cursor3.execute('use meetup_db')
        #cursor.execute('select * from markers')

        eventid = self.request.get('eventid')
        user_list = self.request.get('userlist')
        start_time = self.request.get('starttime')
        end_time = self.request.get('endtime')
        createdby = self.request.get('createdby')

        user_list = user_list.split(',')
        user_list_new=[]
        votes = []
        etas = "Not yet started"
        for u in user_list:
            query = "select userid from users where username = '%s'"%(u)
            cursor2.execute(query)
            user_list_new.append(cursor2.fetchall()[0][0])
            votes.append('-1')
            etas = etas + "|" + "Not yet started"

        timestamp = int(time.time())
        query = "insert into history (eventid,invited,starttime,endtime, votes, eventlastmodified, createdby, eventstatus, usereta) values ('%s','%s', %s, %s, '%s', '%s', '%s', 'Pending', '%s')"%(eventid,"|".join(user_list_new),start_time,end_time, "|".join(votes), timestamp, createdby, etas)
        cursor.execute(query)
        db.commit()
        sendObj = {}
        sendObj['status'] = "success"
        self.response.out.write(json.dumps(sendObj))

app = webapp2.WSGIApplication([
    ('/createevent', MainPage),
], debug=True)

# [END all]
