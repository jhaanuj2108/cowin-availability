
import requests
import time
from SlotById import SlotAvailableByID
from Notify import Notify
import requests
import datetime
import pandas as pd
from firebase_admin import credentials
from firebase_admin import firestore
import firebase_admin

import warnings
warnings.filterwarnings("ignore")

cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

df_pincode = pd.DataFrame(columns=['email','pincode', 'optin', 'type','last_sent_mail','no_of_mails_sent'])
df_district = pd.DataFrame(columns=['email','district', 'optin','type', 'last_sent_mail', 'no_of_mails_sent'])

dict_pincode = dict()
dict_district = dict()

firebase_counter = 0

def get_endpoint_data_to_pandas(users_table):
    global df_pincode
    global df_district
    dict_pincode.clear()
    dict_district.clear()

    for each in users_table.stream():
        print("Taking data from Firebase")
        data_dict = dict()
        if each.to_dict()['type'] == "1":
            pincode = each.to_dict()['pincode']
            email = each.to_dict()['email']
            data_dict['email'] = each.to_dict()['email']
            data_dict['pincode'] = each.to_dict()['pincode']
            data_dict['optin'] = each.to_dict()['optin']
            data_dict['last_sent_mail'] = ''
            data_dict['type'] = each.to_dict()['type']
            data_dict['no_of_mails_sent'] = 0

            df_pincode = df_pincode.append(data_dict, ignore_index=True)
            users_table.document(each.id).delete()

        elif each.to_dict()['type'] == "2":
            district_id = each.to_dict()['district']
            email = each.to_dict()['email']
            data_dict['email'] = each.to_dict()['email']
            data_dict['district'] = each.to_dict()['district']
            data_dict['optin'] = each.to_dict()['optin']
            data_dict['last_sent_mail'] = ''
            data_dict['type'] = each.to_dict()['type']
            data_dict['no_of_mails_sent'] = 0

            df_district = df_district.append(data_dict, ignore_index=True)
            users_table.document(each.id).delete()

    remove_duplicates()

def remove_duplicates():
    global df_pincode
    global df_district
    df_district.drop_duplicates(inplace=True)
    df_pincode.drop_duplicates(inplace=True)
    print("Duplicates Removed")


def create_dict():
    global df_pincode
    global df_district
    dist_list = df_district['district'].unique()
    pin_list = df_pincode['pincode'].unique()
    print("Unique Dictionary created")
    return dist_list, pin_list

def get_email_and_index(type, value):
    global df_pincode
    global df_district
    if type == 'pincode':
        df = df_pincode
    elif type == 'district':
        df = df_district
    time_now = datetime.datetime.now()
    try:
        to = df[(df[type] == value) & (df['optin'] == '1') & (
                int((time_now - df['last_sent_mail']).seconds / 3600) >= 2) & (df['no_of_mails_sent'] < 10)]['email'].values
        index = df[(df[type] == value) & (df['optin'] == '1') & (
                    int((time_now - df['last_sent_mail']).seconds / 3600) >= 2) & (df['no_of_mails_sent'] < 10)].index

    except:
        to = df[(df[type] == value) & (df['optin'] == '1') & (
                df['no_of_mails_sent'] < 10)]['email'].values
        index = df[(df[type] == value) & (df['optin'] == '1') & (
                df['no_of_mails_sent'] < 10)].index

    return to.tolist(), index.tolist()

def check_availabilty_pincode(pin_list):
    for pincode in pin_list:
        pin_obj = SlotAvailableByID(target=pincode, mode = "Pin")
        pin_obj.get_slot_availability()
        flag, hospital, slots, age, date = pin_obj.return_list[0], pin_obj.return_list[1], pin_obj.return_list[2], pin_obj.return_list[3],pin_obj.return_list[4]
        if flag == True:
            to, index = get_email_and_index('pincode', pincode)
            email_obj = Notify(to, hospital, slots, age, date)
            if email_obj.send_mail():
                change_dataframe_data('pincode', index)

def check_availabilty_district(dist_list):
    for district_id in dist_list:
        dist_obj = SlotAvailableByID(target=district_id, mode = "District")
        dist_obj.get_slot_availability()
        flag, hospital, slots, age, date = dist_obj.return_list[0], dist_obj.return_list[1], dist_obj.return_list[2], dist_obj.return_list[3], dist_obj.return_list[4]
        if flag == True:
            to, index = get_email_and_index('district', district_id)
            email_obj = Notify(to, hospital, slots, age, date)
            if email_obj.send_mail():
                change_dataframe_data('district', index)


def change_dataframe_data(type, index):
    global df_pincode
    global df_district
    if type == 'pincode':
        df = df_pincode
    elif type == 'district':
        df = df_district

    df.iloc[index, [4]] = datetime.datetime.now()
    df.iloc[index, [5]] = df.iloc[index, [5]] + 1

    counter_index = df.iloc[index][df['no_of_mails_sent'] == 5].index
    df.iloc[counter_index, [2]] = 0


def save_in_local():
    global df_pincode
    global df_district
    df_district.to_csv('district.csv',index=False)
    df_pincode.to_csv('pincode.csv',index=False)



def remove_from_firebase(id_list, to):
    url = "https://cowin-realpython.herokuapp.com/testUpdate?id="

    for i in range(len(id_list)):
        new_url = url + id_list[i]
        requests.post(new_url)
        print('Removed: \n\tEmail:'+to[i] +' \n\tUID:'+id_list[i]+'\n')


def saving_to_firebase():
    for i in range(len(df_district)):
        data = df_district.iloc[i].to_dict()
        db.collection('backupCowin').add(data)

    for i in range(len(df_pincode)):
        data = df_pincode.iloc[i].to_dict()
        db.collection('backupCowin').add(data)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    flag_first_time = input("Is this the first time? 1/0: ")

    while True:
        try:
            from datetime import date
            test_url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=294&date="
            test_date = date.today().strftime('%d-%m-%Y')
            test_url += test_date


            # try:
            test_response = requests.get(test_url, headers={"accept": "application/json", "Accept-Language": "hi_IN",
                                                          "user-agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"}).json()['centers']
            # print("Cowin API Working")
            if flag_first_time == 1:
                df_pincode = pd.read_csv('pincode.csv')
                df_district = pd.read_csv('district.csv')

            usersRef = db.collection('cowinUsers')
            testusersRef = db.collection('testCowinUsers')
            users_table = usersRef
            get_endpoint_data_to_pandas(users_table)
            save_in_local()

            dist_list, pin_list  = create_dict()
            check_availabilty_pincode(pin_list)
            check_availabilty_district(dist_list)
            save_in_local()

            firebase_counter += 1

            if firebase_counter == 12:
                saving_to_firebase()
                firebase_counter = 0

            print("5 min break")
            time.sleep(300)
        except:
            print("Cowin API Down")
            print("5 min break")
            time.sleep(300)