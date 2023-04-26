from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import requests

import datetime

import config

transport = AIOHTTPTransport(
    url=config.ROSESLIVE_API_URL,
    headers = {
    "Authorization": config.ROSESLIVE_API_KEY
    }
)
client = Client(transport=transport, fetch_schema_from_transport=True)

def publish(title: str, url: str, catch_up: bool) -> str:
    try:
        id = client.execute(gql("""
    mutation {
    createVideoLink (data: {
        title: "%s",
        url: "%s",
        liveFrom: "%s",
        liveUntil:"%s",
        catchUp:%s
    }) {
        id
    }
    }
    """ % (title, 
        url, 
        datetime.datetime.now().astimezone().isoformat(), 
        (datetime.datetime.now().astimezone() + datetime.timedelta(days=1)).isoformat(), 
        "true" if catch_up else "false")))["createVideoLink"]["id"]

        client.execute(gql("""
        mutation {
        publishVideoLink (where: {
            id: "%s"
        },to: PUBLISHED
        ) {
            stage
        }
        }
        """ % (id)))


        return id

    except Exception as err:
        print(err)
        return ""

def delete(id: str):
    client.execute(gql("""
mutation {
  deleteVideoLink(where:{
    id: "%s"
  }) {
    stage
  }
}
""" % (id)))

def change_to_catchup(id: str, title: str, catchup_url: str):
    
    delete(id)
    publish(title, catchup_url, True)


#     client.execute(gql("""
#     mutation {
#   updateVideoLink(where: {
#     id: "%s"
#   }, data: {
#     title: "%s",
#     url: "%s",
#     catchUp: true
#   }) {
#     id
#   }
# }
# """ % (id, title, catchup_url)))

def request_log(stream_endpoint: str, start_time, end_time, name) -> str:
    return requests.post(config.LOG_REQUEST_URL, json = {
        "name": f"{name} - Full Commentary",
        "startTime": start_time.astimezone().isoformat(),
        "endTime": end_time.astimezone().isoformat(),
        "stream": f"roses-out-{stream_endpoint}"
    }).text