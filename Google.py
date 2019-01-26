""" Google API"""
from __future__ import print_function
from googleapiclient.discovery import build
import googleapiclient
from httplib2 import Http
from oauth2client import file, client, tools
import datetime
from YNAB import *
from dateutil.parser import parse
import requests
import json
import aws

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

"""Pulls events since last sync and searches for 'ynab' in first line of the description. Pulls those events out and 
processes them for sending to YNAB as transactions. 
"""
store = file.Storage('token.json')
#creds = client.GoogleCredentials.get_application_default()
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))

now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time


# Pulls the sync token and stores it in the user profile in dynamodb to be used later
def get_sync_token(items_from_calendar):
    sync_token = items_from_calendar['nextSyncToken']
    aws.table.update_item(
        Key={
            'user': '1'
        },
        UpdateExpression='SET google_sync_token = :val1',
        ExpressionAttributeValues={
            ':val1': sync_token
        }
    )
    return sync_token


# This is for times if the current synctoken doesn't work and a full sync is needed to repair / refresh the sync token
def get_synctoken_from_full_sync():
    events = service.events().list(calendarId='primary').execute()
    while 'nextPageToken' in events.keys():
        next_page = events['nextPageToken']
        events = service.events().list(calendarId='primary', pageToken=next_page).execute()
    sync_token = events['nextSyncToken']
    aws.table.update_item(
        Key={
            'user': '1'
        },
        UpdateExpression='SET google_sync_token = :val1',
        ExpressionAttributeValues={
            ':val1': sync_token
        }
    )
    return sync_token


# The function to pull the events and send off to YNAB.
def post_to_ynab():
    try:
        events_result = service.events().list(calendarId='primary', syncToken=aws.get_item['google_sync_token']).execute()
        get_sync_token(events_result)
        events = events_result.get('items', [])
        get_ynab_events(events)
    except googleapiclient.discovery.HttpError as x:
        if '410' in str(x):
            print('Initiating full sync')
            get_synctoken_from_full_sync()
        else:
            print(x)

# Pull out the third line of the calendar event description
def get_third_line(description):
    amount = description.split('\n')[2]
    return amount

# Pull out the second line of the calendar event description
def get_second_line(description):
    category = description.split('\n')[1]
    return category

# searches for events that have 'ynab' in the descriptions and configures then sends them to YNAB as transactions
def get_ynab_events(events):
    for event in events:
        if event.get('description') and 'ynab' in event.get('description'):
            date_and_time = event['start'].get('dateTime', event['start'].get('date'))
            date = parse(date_and_time).date()
            category_id = get_category_id(get_second_line(event['description']))
            amount = str(int(float(get_third_line(event['description']))) * 1000 * -1)
            today = datetime.date.today().strftime('%Y-%m-%d')
            summary = event['summary']
            import_id = str(date) + amount + summary
            memo = f'{summary} \n {date}'
            data = json.dumps({"transaction": {"account_id": main_budget.account_id(), "date": today, "amount": amount,
                                               "category_id": category_id, "memo": memo, "cleared": "cleared",
                                               "approved": True, "flag_color": "red", "import_id": import_id}})
            print(requests.post(f'https://api.youneedabudget.com/v1/budgets/{specific_budget_id(budget)}/transactions',
                          headers=headers, data=data).json())



def lambda_handler(event, context):
    post_to_ynab()


post_to_ynab()