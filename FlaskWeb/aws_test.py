APP_ID = 'AKIAW3O3WBDDQSPPNNNZ'
APP_KEY = 'xJO6tjbUrKw6ulxGV7i6jjOTtSMyY5YzlIpmj+sL'

import boto3

dynamodb = boto3.resource("dynamodb", aws_access_key_id=APP_ID,
                          aws_secret_access_key=APP_KEY, region_name="ap-southeast-2")
tableInfo = dynamodb.Table("sounddata").scan()

for i in tableInfo['Items']:
    print(i)
    print(i['payload']['currentTime'])
    print(i['payload']['soundVal'])
    print(i['payload']['deviceID'])
