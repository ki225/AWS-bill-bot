import json
import boto3
import telebot
import requests
from datetime import datetime, timedelta

TOKEN = "6480485818:AAHyiYyC3JwlHDq3rjGLEkG_Ojeqq6ny5R8" # <YOUR_TELEGRAM_BOT_TOKEN>
bot = telebot.TeleBot(TOKEN)

def lambda_handler(event, context):
    body=json.loads(event['body'])
    print("the input is ",body)
    message_part=body['message'].get('text')
    chat_id=body['message']['chat']['id']
    reply=""

    try:
        client = boto3.client('ce') # AWS Cost Explorer
        end_date = datetime.strptime(message_part, '%Y-%m-%d')
        start_date = datetime.strptime(message_part[:8]+"01", '%Y-%m-%d')
        # usage and cost
        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],  # the raw cost of a resource before any discounts or credits are applied
        )
        
        results = response['ResultsByTime']
        print(results)
        reply += f"Your total bill amount from {results[0]['TimePeriod']['Start']} to {results[0]['TimePeriod']['End']} is: " + str(results[0]['Total']['UnblendedCost']['Amount']) + " " + results[0]['Total']['UnblendedCost']['Unit'] + ".\n"
        if float(results[0]['Total']['UnblendedCost']['Amount'])>0:
            response = client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],  # the raw cost of a resource before any discounts or credits are applied
                GroupBy=[
                    {
                        'Type':'DIMENSION',
                        'Key':'SERVICE'
                    }
                ]
            )
            # print(response)
            for service in response['ResultsByTime'][0]['Groups']:
                if float(service['Metrics']['UnblendedCost']['Amount'])>0:
                    keys = service['Keys']
                    amount = service['Metrics']['UnblendedCost']['Amount']
                    # print(f"項目：{keys[0]}, 金額：{amount}")
                    reply+=f"service:{keys[0]}, cost:{amount}\n"

        print(reply)
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={reply}"
        print(requests.get(url).json())
        
        return {
            'statusCode': 200,
        }
    except:
        reply += "Sorry, please input a valid date in the format YYYY-MM-DD."
        print("An error occurred")
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={reply}"
        print(requests.get(url).json())
        return {
            'statusCode': 200,
        }
    



