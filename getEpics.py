import json
import csv
import requests
from datetime import datetime
import config
import re


print("Start:" + datetime.now())

urlJira = config.jiraAccess['url']
usuario = config.jiraAccess['username']
senha = config.jiraAccess['password']
paramFields = config.jiraParam['fields']
paramMax = config.jiraParam['max']
project = config.jiraParam['key']
issuesType = config.jiraParam['issuetype']

headers = {
    'Accept': '*/*',
    'User-Agent': 'request',
}

#https://jira.bradesco.com.br:8443/rest/api/2/project/OPBAN9/statuses

testeEpico = {}
if bool(testeEpico):
    print(testeEpico)
testeEpico["Validado"] = 11

""" resultStatus = requests.get(urlJira + 'rest/api/2/project/' + project + '/statuses', headers=headers, auth=(usuario, senha))
jsonStatus = json.loads(resultStatus.text)
for status in jsonStatus:
    if status['name'] == 'Epic':
        for workflow in status['statuses']:
            print(workflow['name']) 
            statusName = str(workflow['name'])
            if  statusName in testeEpico.keys():
                testeEpico[statusName] = testeEpico[statusName] + 1
            else:
                testeEpico[statusName] = 1

print(testeEpico) """

startAt = 0
maxResults = 0
total = 1

listEpics = []
rowEpic = []

headerEpics = ["key","summary","status"]
with open(r'epics.csv', 'w') as f:
    f.truncate()
    writer = csv.writer(f,dialect='excel')
    writer.writerow(headerEpics)

    while (startAt < total):
        try:
            epicsResult = requests.get(urlJira + 'rest/api/2/search?jql=project=' + project + ' and issuetype in (epic)&startAt='+ str(startAt) + '&fields=key,summary,status' + paramMax, headers=headers, auth=(usuario, senha))
            jsonResult = json.loads(epicsResult.text)
        except: 
            print("error")
        finally:
            maxResults = int(jsonResult['maxResults'])
            startAt = int(jsonResult['startAt']) + maxResults
            total = int(jsonResult['total'])

            for resultJson in jsonResult['issues']:
                rowEpic.append(resultJson['key'])
                rowEpic.append(re.sub('\t+', ' ', resultJson['fields']['summary']))
                rowEpic.append(resultJson['fields']['status']['name'])
                writer.writerow(rowEpic)

                rowEpic.clear()
                listEpics.append(resultJson['key'])


transitions = ["key","created","actualStatus","moved","fromStatus","toStatus"]
with open(r'epicsTransitions.csv', 'w') as fi:
    fi.truncate()
    writerTransitions = csv.writer(fi,dialect='excel')
    writerTransitions.writerow(transitions)
    transitions.clear()

    rowTransition = []
    for epic in listEpics:
        try:
            msgRequest = requests.get(urlJira + 'rest/api/2/issue/' + epic + '?expand=changelog&fields=' + paramFields , headers=headers, auth=(usuario, senha))
            jsonMsg = json.loads(msgRequest.text)
        except:
            print('error')
        finally:
            for histories in jsonMsg['changelog']['histories']:
                for item in histories['items']:
                    if item['field'] == 'status':
                        rowTransition.append(epic)
                        rowTransition.append(datetime.strptime(jsonMsg['fields']['created'].split(".")[0], '%Y-%m-%dT%H:%M:%S'))
                        rowTransition.append(jsonMsg['fields']['status']['name'])
                        rowTransition.append(datetime.strptime(histories['created'].split(".")[0], '%Y-%m-%dT%H:%M:%S'))
                        rowTransition.append(item['fromString'])
                        rowTransition.append(item['toString'])

                        writerTransitions.writerow(rowTransition)
                        rowTransition.clear()
print("Stop:" + datetime.now())