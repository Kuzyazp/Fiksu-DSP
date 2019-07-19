import boto3
import time
import subprocess

# Create SQS client
SQS_QUEUE_URL='https://sqs.eu-central-1.amazonaws.com/907208926079/test-queue'

print('SQS_QUEUE_URL')
sqs = boto3.client('sqs')

queue_url = 'https://sqs.eu-central-1.amazonaws.com/907208926079/test-queue'

# Send message to SQS queue
response = sqs.send_message(
    QueueUrl=queue_url,
    DelaySeconds=0,
    MessageAttributes={
        'Title': {
            'DataType': 'String',
            'StringValue': 'The Whistler'
        },
        'Author': {
            'DataType': 'String',
            'StringValue': 'John Grisham'
        },
        'WeeksOn': {
            'DataType': 'Number',
            'StringValue': '6'
        }
    },
    MessageBody=(
        'Information about current NY Times fiction bestseller for '
        'week of 12/11/2016.'
    )
)

print(response['MessageId'])

#Receive message from SQS

response = sqs.receive_message(
    QueueUrl=queue_url,
    AttributeNames=[
        'SentTimestamp'
    ],
    MaxNumberOfMessages=1,
    MessageAttributeNames=[
        'All'
    ],
    VisibilityTimeout=5,
    WaitTimeSeconds=0
)

message = response['Messages'][0]
receipt_handle = message['ReceiptHandle']

#Start background process

backgroundtask = subprocess.Popen(['./background_process.sh'])
time.sleep(1)

#Read the flag value:
with open('Flag_status.txt') as f:
    flag_status = f.readline()

print flag_status

time_offset=5

while flag_status <> '1\n':
    #Invrease visibility
    sqs.change_message_visibility(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle,
        VisibilityTimeout=time_offset
    )
    print('Changed visibility timeout of message')
    #Check the flag status:
    with open('Flag_status.txt') as f:
        flag_status = f.readline()
    print flag_status
    time.sleep(5)
    time_offset += 5

# Delete received message from queue
sqs.delete_message(
    QueueUrl=queue_url,
    ReceiptHandle=receipt_handle
)
print('Deleted message: %s' % message)

# Delete SQS queue
#sqs.delete_queue(QueueUrl='SQS_QUEUE_URL')
