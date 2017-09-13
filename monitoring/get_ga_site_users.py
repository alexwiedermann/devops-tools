import argparse

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import httplib2
import json
from oauth2client import client
from oauth2client import file
from influxdb import InfluxDBClient
from oauth2client import tools

def get_service(api_name, api_version, scope, key_file_location,
                service_account_email):
  credentials = ServiceAccountCredentials.from_p12_keyfile(service_account_email, key_file_location, scopes=scope)
  http = credentials.authorize(httplib2.Http())
  service = build(api_name, api_version, http=http)
  return service

def main():
  scope = ['https://www.googleapis.com/auth/analytics.readonly']
  service_account_email = "xxxxx@developer.gserviceaccount.com"
  key_file_location = "key.p12"

  service = get_service('analytics', 'v3', scope, key_file_location,
  service_account_email)

  results = service.data().realtime().get(
      ids='ga:xxxxxx',
      metrics='rt:activeUsers',
      dimensions='rt:medium').execute()
  print results['totalsForAllResults']['rt:activeUsers']
  activeusers = results['totalsForAllResults']['rt:activeUsers']

def toinfluxdb(host='localhost', port=8086, dbname='activeusers', activeusers=activeusers):
  json_body = [
    {
        "value": activeusers,
    }
    ]
  client.write_points(json_body)

if __name__ == '__main__':
  main()
