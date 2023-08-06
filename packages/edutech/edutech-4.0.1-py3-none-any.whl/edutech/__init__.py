import boto3
import uuid
import json
sns = boto3.client('sns')

client = boto3.client('dynamodb')

def update_notification(tableName,user_ids,notification_type,notification_message):
     notification_ids = str(uuid.uuid4())
     res = client.put_item(
        TableName=tableName,
        Item={
            'notification_ids': {
                'S': notification_ids
            },

            'user_ids': {
                'S': user_ids
            },

            'notification_type': {
                'S': notification_type
            },

            'notification_message': {
                'S': notification_message
            },
        }
    )


def send_notification(arn,title,message):
    GCM_data={"notification": { "body": message,"title": title } }
    data={
        "default" : "test",
        "GCM": json.dumps(GCM_data)
        }
    publish_result = sns.publish(
        TargetArn=arn,
        MessageStructure='json',
        Message=json.dumps(data),
        )




