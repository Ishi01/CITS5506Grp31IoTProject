from flask import Flask, render_template, jsonify
import boto3

app = Flask(__name__)

APP_ID = 'AKIAW3O3WBDDQSPPNNNZ'
APP_KEY = 'xJO6tjbUrKw6ulxGV7i6jjOTtSMyY5YzlIpmj+sL'


def getAwsInfo():
    dynamodb = boto3.resource("dynamodb", aws_access_key_id=APP_ID,
                              aws_secret_access_key=APP_KEY, region_name="ap-southeast-2")
    tableInfo = dynamodb.Table("soundfinal").scan()
    result = []
    for i in tableInfo['Items']:
        try:
            result.append(i['payload'])
        except KeyError as e:
            pass
    return result


def getAwsNewData():
    dynamodb = boto3.resource("dynamodb", aws_access_key_id=APP_ID,
                              aws_secret_access_key=APP_KEY, region_name="ap-southeast-2")
    tableInfo = dynamodb.Table("soundfinal").scan()
    result = []
    for i in tableInfo['Items']:
        try:
            result.append(i['payload'])
        except KeyError as e:
            pass
    maxVal = max(result, key=lambda j: j['currentTime'])
    return maxVal


@app.route('/')
def hello_world():
    return render_template('screen.html')


@app.route('/getData')
def getData():
    res = getAwsInfo()
    x = []
    y = []
    sortVal = sorted(res, key=lambda j: j['currentTime'])
    for i in sortVal[:1800]:
        if "currentTime" in i:
            x.append(i['currentTime'])
            y.append(i['soundVal'])

    return jsonify({"x": x, "y": y})


@app.route('/getNewData')
def getNewData():
    res = getAwsNewData()
    gauge1 = round((res['sensor1'] * 350 + 10) / 150, 2)
    gauge2 = round((res['sensor2'] * 350 + 10) / 150, 2)
    return jsonify({"gauge1": gauge1, "gauge2": gauge2})


if __name__ == '__main__':
    app.run()
