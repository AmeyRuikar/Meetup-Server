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
os.system("sudo pip install -U googlemaps")
import MySQLdb
import webapp2
import json
import distance_matrix as d





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


class MainPage(webapp2.RequestHandler):
    def get(self):
        """Simple request handler that shows all of the MySQL variables."""
        self.response.headers['Content-Type'] = 'text/plain'
        try:
            import googlemaps

            key = 'AIzaSyCXpUMDiQ4_7NeQdUR-bL9ToVvYH2f64vU'
            client = googlemaps.Client(key)
            origins = ["Bobcaygeon ON", [41.43206, -81.38992]]
            destinations = [(43.012486, -83.6964149),{"lat": 42.8863855, "lng": -78.8781627}]
            d1 = d.distance_matrix(client, origins, destinations,mode=None, language=None, avoid=None, units=None,departure_time=None, arrival_time=None, transit_mode=None,transit_routing_preference=None, traffic_model=None)
            self.response.out.write(str(d1))
        except Exception:
            self.response.out.write("caught exception")
        '''
        obj = {
            'status':'success',
            'db':'cloud SQL'

        }
        self.response.out.write(json.dumps(obj))
        '''


app = webapp2.WSGIApplication([
    ('/etatest', MainPage),

], debug=True)

# [END all]
