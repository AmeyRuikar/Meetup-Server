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

class insert(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'

        db = connect_to_cloudsql()
        cursor = db.cursor()

        obj = {
            'status': 'success'
        }

        self.response.out.write(json.dumps(obj))

# https://meetup-server-150406.appspot.com/spatial?points=0%200,50%20100,100%200,%2050%20-100,%200%200
class MainPage(webapp2.RequestHandler):
    def get(self):
        """Simple request handler that shows all of the MySQL variables."""
        #self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Content-Type'] = 'application/json'

        db = connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute('use meetup_db')
        xlocation = self.request.get('x')
        ylocation = self.request.get('y')
        X = float(xlocation)
        Y = float(ylocation)
        # stringlocation = '0 0,50 100,100 0, 50 -100, 0 0'
        # cursor.execute("select eventname from events where ST_WITHIN(eventlocation, ST_GeomFromText('POLYGON(("+ markerlocation +"))'))")
        #markerlocation = [xlocation ylocation-0.4, xlocation+0.4 ylocation, xlocation ylocation+0.4, xlocation-0.4 ylocation, xlocation ylocation-0.4]
        #markerlocationstring =
        markerlocation = '%f %f,%f %f,%f %f,%f %f,%f %f'%((X+0.09),Y,X,(Y-0.09),(X-0.09),Y, X, (Y+0.09),(X+0.09),Y)

        cursor.execute("select eventname,genre from events where ST_WITHIN(eventlocation, ST_GeomFromText('POLYGON(("+ markerlocation +"))'))")

        retrievedEvents = []
        cnt = 3;

        for r in cursor.fetchall():
            #self.response.write('{}\n'.format(r))
            #self.response.write('{}\n'.format(r[0]+"-"+r[6]))
            if r[1] =='food':
                retrievedEvents.append("try dishes from " + r[0])
                cnt = cnt -1
            elif r[1] == 'Music' or r[1]== 'Arts & Theatre':
                retrievedEvents.append("try the event at " + r[0])
                cnt = cnt -1
            elif r[1] == 'Sports':
                retrievedEvents.append("Sports Fan? Catch this game " + r[0])
                cnt = cnt -1
            else:
                pass
            if cnt == 0:
                break
            '''
            retrievedEvents.append("try the event at " + r[0])
            break
            '''


        '''
        obj = {
            'status':'success',
            'db':'cloud SQL'

        }
        self.response.out.write(json.dumps(obj))
        '''
        self.response.out.write(json.dumps(retrievedEvents))


app = webapp2.WSGIApplication([
    ('/adsense', MainPage),

], debug=True)

# [END all]
