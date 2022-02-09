jiraAccess = dict(
    username = 'm232682',
    password = 'senha01',
    url = 'https://jira.bradesco.com.br:8443/'
)
jiraParam = dict(
    key = 'ARPOS,ARARQ,ARARI,ARASP,ARDAL,ARFAG,ARINV,ARPOR,PVTOD,ARBKR,ARSRE',
    fields = 'worklog,summary,issuetype,key,status,created,customfield_12318,customfield_10214',
    max = '&maxResults=100',
    issuetype = 'Epic'
)