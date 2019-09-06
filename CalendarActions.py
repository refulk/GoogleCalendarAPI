###############################################################################################################
################  READ ME  #######################
# NECESSARIO PARA O FUNCIONAMENTO:
# Siga o tutorial: https://developers.google.com/calendar/quickstart/python?refresh=1&pli=1
# Ponto importante do tutorial:
# 1 - Caso ainda NAO tenha as credenciais: ENABLED THE GOOGLE CALENDAR API (download client configuration e renomeie o arquivo para 'client_secret.json', salve no mesmo diretorio deste codigo)
# 2 - EXECUTE: pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# 
# Outros links, utilizados para consulta e desenvolvimento:
# > Tutorial google:
# https://developers.google.com/calendar/ 
# > Ensina a ler e inserir eventos
# https://www.youtube.com/watch?v=j1mh0or2CX8 
# > Documentacao, referencia (comandos):
# https://developers.google.com/calendar/v3/reference/events/insert
###############################################################################################################

from __future__ import print_function
from datetime import datetime, timedelta
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class CalendarActions:
    # AUTENTICACAO
    def __init__(self):
        # If modifying these scopes, delete the file token.pickle.
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)
        self.timezone = 'Brazil/East'

    # exibe os eventos apos a leitura de dados ter sido feita
    def showEvents(self, events):
        print('Events:')
        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

    # LEITURA DE DADOS
    # eh possivel filtrar por advogado, atraves de seu email
    def getEvents(self, startDate, qtdDays, emailFilter=None):
        returnQuery = []
        endDate = startDate + timedelta(days=qtdDays)
        startDate = startDate.isoformat() + 'Z' # 'Z' indicates UTC time 
        endDate = endDate.isoformat() + 'Z' # 'Z' indicates UTC time

        #Get My Calendars
        #events_result = service.calendarList().list().execute()
        #print (events_result['items'][0])
        #print (events_result['items'][0]['id']) #id from calendar (email)

        #Get My Calendar Events
        #print('Getting events')
        events_result = self.service.events().list(calendarId='primary', timeMin=startDate,
                                            timeMax=endDate, singleEvents=True,
                                            orderBy='startTime', timeZone=self.timezone).execute()
        events = events_result.get('items', [])   

        #Filtra por email caso events e emailFilter nao sejam vazios
        if events and emailFilter != None:
            for event in events:
                for email in event['attendees']:
                    email = str(email)
                    if emailFilter in email:
                        returnQuery.append(event)                
            return returnQuery
        else: #Caso contrario retorna o resultado da query sem passar pelo filtro
            return events

    # INSERCAO DE UM NOVO EVENTO
    def createEvent(self, startDate, summary, email, email2, durationHours=1, location=None, description=None):
        endDate = startDate + timedelta(hours = durationHours)
        
        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': startDate.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': self.timezone,
            },
            'end': {
                'dateTime': endDate.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': self.timezone,
            },
            'recurrence': [
                #'RRULE:FREQ=DAILY;COUNT=3' #frequency and how many days
            ],
            'attendees': [
                {'email': email}, #invite someone to an event
                {'email': email2}, #invite someone to an event
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                {'method': 'email', 'minutes': 24 * 60}, #email 24 hours before event
                {'method': 'popup', 'minutes': 10}, #pop up 10 minutes before event
                ],
            },
        }
        event = self.service.events().insert(calendarId='primary', body=event).execute()
        #print ('Event created: %s' % (event.get('htmlLink')))

    # DELETAR EVENTO
    # eh preciso primeiramente realizar uma consulta para obter o ID do evento
    # o ID eh passado como parametro e entao eh feita a exclusao
    def deleteEvent(self, id):
        try:
            self.service.events().delete(calendarId='primary', eventId=id).execute()
            return 1 #deletou com sucesso
        except:
            return 0 #nao foi possivel deletar

#Funcao main contem exemplos do uso das funcoes
if __name__ == '__main__':
    ### Define object #############
    calendar = CalendarActions()
    ###############################

    ### Create an event #########################################################################
    startDate = datetime(2019,9,6,10,0,0) #year month day hour minute second
    calendar.createEvent(startDate, "summary", "advogado@email.com", "cliente@email.com", 0.5, "location", "description")    
    #############################################################################################

    ### Get all events in next 5 days ######################################
    startDate = datetime.utcnow()
    qtdDays = 5
    #events = calendar.getEvents(startDate, qtdDays, "advogado@email.com") # com filtro por email
    events = calendar.getEvents(startDate, qtdDays)  #sem filtro
    ########################################################################

    ### Display query result ####
    calendar.showEvents(events)
    #############################

    ### Get first event id #######
    if events:
        idExc = events[0]['id']
    else:    
        idExc = None
    #############################

    ### Delete first event, if it exists ####
    # 0 > fail
    # 1 > sucess
    print(calendar.deleteEvent(idExc)) # aelu68kkrrvaffl7tei35uh51c  >> id example
    #########################################

    events = calendar.getEvents(startDate, qtdDays)  #apos excluir consulta novamente
    calendar.showEvents(events)
    #print(events)