import json
import csv
import requests
from datetime import datetime
import config
import re


print("Start:")
print(datetime.now())

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

startAt = 0
maxResults = 0
total = 1

listStory = []
rowStory = []

dataAtivado = ""

headerStory = ["key","summary","status","Ponto de Função","Time","issuesType","DataAtivado","MesAtivado"]
with open(r'story.csv', 'w') as f:
    f.truncate()
    writer = csv.writer(f,dialect='excel')
    writer.writerow(headerStory)

    while (startAt < total):
        try:
            epicsResult = requests.get(urlJira + 'rest/api/2/search?jql=project in (' + project + ') and created < 2021-12-31 AND filter = 29914 and issuetype in standardIssueTypes() and cf[12318] is not EMPTY and statusCategory = Done&startAt='+ str(startAt) + '&fields=key,summary,status,customfield_12318,customfield_10214,issuetype' + paramMax, headers=headers, auth=(usuario, senha))
            jsonResult = json.loads(epicsResult.text)
        except: 
            print("error")
        finally:
            maxResults = int(jsonResult['maxResults'])
            startAt = int(jsonResult['startAt']) + maxResults
            total = int(jsonResult['total'])

            for resultJson in jsonResult['issues']:
                rowStory.append(resultJson['key'])
                rowStory.append(re.sub('\t+', ' ', resultJson['fields']['summary']))
                rowStory.append(resultJson['fields']['status']['name'])
                rowStory.append(resultJson['fields']['customfield_12318'])
                rowStory.append(resultJson['fields']['customfield_10214'])
                rowStory.append(resultJson['fields']['issuetype']['name'])                
                try:
                    transitionResult = requests.get(urlJira + 'rest/api/2/issue/' + resultJson['key'] + '?expand=changelog&fields=changelog&fields=changelog' + paramMax, headers=headers, auth=(usuario, senha))
                    jsonTransition = json.loads(transitionResult.text)
                except:
                    print("Error Transition")
                finally:
                    for transition in jsonTransition['changelog']['histories']:
                        for item in transition['items']:
                            if item['field'] == 'status' and item['from'] == '10402' and item['to'] == '10114':
                                dataAtivado = datetime.strptime(transition['created'].split(".")[0], '%Y-%m-%dT%H:%M:%S')
                                mesAtivado = datetime.strptime(transition['created'].split(".")[0], '%Y-%m-%dT%H:%M:%S').month
                                anoAtivado = datetime.strptime(transition['created'].split(".")[0], '%Y-%m-%dT%H:%M:%S').year
                                break
                            if item['field'] == 'status' and item['to'] == '10102':
                                dataAtivado = datetime.strptime(transition['created'].split(".")[0], '%Y-%m-%dT%H:%M:%S')
                                mesAtivado = datetime.strptime(transition['created'].split(".")[0], '%Y-%m-%dT%H:%M:%S').month
                                anoAtivado = datetime.strptime(transition['created'].split(".")[0], '%Y-%m-%dT%H:%M:%S').year
                                break
                        if dataAtivado : 
                            rowStory.append(dataAtivado)
                            rowStory.append(datetime(anoAtivado,mesAtivado,1).strftime("%B/%Y"))
                            dataAtivado = ""
                            mesAtivado = ""
                            anoAtivado = ""
                            break
                writer.writerow(rowStory)
                rowStory.clear()

print('Carregar Lista Worklog')
print(datetime.now())

startAt = 0
maxResults = 0
total = 1
while (startAt < total):
    try:
        epicsResult = requests.get(urlJira + 'rest/api/2/search?jql=project in (' + project + ') and worklogDate < "2021-12-31" AND filter = 29914 and timespent > 0 and worklogDate >= "2021-09-01"&startAt='+ str(startAt) + '&fields=key,summary,status,customfield_12318,customfield_10214' + paramMax, headers=headers, auth=(usuario, senha))
        jsonResult = json.loads(epicsResult.text)
    except: 
        print("error")
    finally:
        maxResults = int(jsonResult['maxResults'])
        startAt = int(jsonResult['startAt']) + maxResults
        total = int(jsonResult['total'])

        for resultJson in jsonResult['issues']:
            listStory.append(resultJson['key'])


print(len(listStory))
print('Lista de Worklog carregada')
print(datetime.now())

transitions = ["key","team","chaveM","nome","worklogDate","WorklogM","timespentSeconds","timespentHour"]
with open(r'storyTransitions.csv', 'w') as fi:
    fi.truncate()
    writerTransitions = csv.writer(fi,dialect='excel')
    writerTransitions.writerow(transitions)
    transitions.clear()

    rowTransition = []
    for story in listStory:
        try:
            msgRequest = requests.get(urlJira + 'rest/api/2/issue/' + story + '?&fields=' + paramFields , headers=headers, auth=(usuario, senha))
            jsonMsg = json.loads(msgRequest.text)
        except:
            print('error')
        finally:
            if len(jsonMsg['fields']['worklog']) >0:
                for worklog in jsonMsg['fields']['worklog']['worklogs']:
                    rowTransition.append(story)
                    rowTransition.append(jsonMsg['fields']['customfield_10214'])
                    rowTransition.append(worklog['author']['key'])
                    rowTransition.append(worklog['author']['displayName'])
                    rowTransition.append(datetime.strptime(worklog['started'].split(".")[0], '%Y-%m-%dT%H:%M:%S'))
                    mesLog = datetime.strptime(worklog['started'].split(".")[0], '%Y-%m-%dT%H:%M:%S').month
                    anoLog = datetime.strptime(worklog['started'].split(".")[0], '%Y-%m-%dT%H:%M:%S').year
                    periodoLog = datetime(anoLog,mesLog,1).strftime('%B/%Y')
                    rowTransition.append(periodoLog)
                    rowTransition.append(worklog['timeSpentSeconds'])
                    rowTransition.append(int(worklog['timeSpentSeconds'])/3600)

                    writerTransitions.writerow(rowTransition)
                    rowTransition.clear()
print("Stop:")
print(datetime.now())