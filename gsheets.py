import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
from datetime import datetime as date
from time import  sleep
def push_worktime(agent,h,m):
    today = date.today().strftime("%A")
    print(today)
    days = {"Monday":13,"Tuesday":14,"Wednesday":15,"Thursday":16,"Friday":17,"Saturday":11,"Sunday":12}
    scope = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
        ]
    file_name = '/home/pi/bot-frat/client_key.json'
    hours = None
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
    client = gspread.authorize(creds)
    sheet = client.open('Suivi Heures').get_worksheet_by_id(2036745914)
    print(dir(sheet))
    print(sheet)
    python_sheet = sheet.get_all_records()
    for i in range (1 ,len(python_sheet)-1):
        if sheet.cell(i,21).value == str(agent):
            print("Agent trouvé !")
            print(sheet.cell(i,21).value)
            value_stored = sheet.cell(i,days[today]).value.split(":")
            hours = value_stored[0]
            hours = int(hours)+int(h)
            minutes = value_stored[1]
            minutes = int(minutes)+int(m)
            if hours < 10 :
                hours = "0"+str(hours)
            if minutes < 10 :
                minutes = "0"+str(minutes)
            sheet.update_cell(i,days[today],str(hours)+":"+str(minutes))
            print("Changement effectué !")
            
def change_week():
    today = date.today().strftime("%A")
    print(today)
    LISTEA = {1:"A",2:"B",3:"C",4:"D",5:"E",6:"F",7:"G",8:"H",9:"I",10:"J",11:"K",12:"L",13:"M",14:"N",15:"O",16:"P",17:"Q",18:"R",19:"S",20:"T",21:"U"}
    dt_string = date.now().strftime("%d/%m/%Y")
    days = {"Monday":13,"Tuesday":14,"Wednesday":15,"Thrusday":16,"Friday":17,"Saturday":11,"Sunday":12}
    scope = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
        ]
    file_name = 'client_key.json'
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
    client = gspread.authorize(creds)
    sheet = client.open('[SAMU] Temps de travail')
    new = client.create("[SAMU] Temps de travail | ARCHIVE DU "+str(dt_string))
    new.share('theo.marechal0@gmail.com', perm_type='user', role='writer')
    sheet.sheet1.copy_to(new.id)
    python_sheet = sheet.sheet1.get_all_records()
    for i in range (1 ,len(python_sheet)-1):
        if sheet.sheet1.cell(i,20).value != None:
            print("Agent trouvé !")
            for j in range(11,18):
                if sheet.sheet1.cell(i,j).value !=  "00:00:00":
                    sheet.sheet1.update_cell(i,j,"00:00:00")
                    sleep(2)
    for i in range (11,18):
        sheet.sheet1.update_cell(9,i,str(date.today() + date.timedelta(days=(i-10))))
        sleep(5)
    print("Changement effectué !")
       
            
push_worktime(572066627382673410,1,2)
#change_week()