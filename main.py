
import requests
import time
from SlotById import SlotAvailableByID
from Notify import Notify
import requests
from firebase_admin import credentials
from firebase_admin import firestore
import firebase_admin
cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

dict_pincode = dict()
dict_district = dict()

def get_endpoint_data(users_table):
    dict_pincode.clear()
    dict_district.clear()
    for each in users_table.stream():
        # print("This is being printed")
        data_dict = dict()
        if each.to_dict()['optin'] == "1":
            if each.to_dict()['type'] == "1":
                pincode = each.to_dict()['pincode']
                email = each.to_dict()['email']

                if pincode in dict_pincode:
                    dict_pincode[pincode][0].append(email)
                    dict_pincode[pincode][1].append(each.id)
                else:
                    dict_pincode[pincode] = list()
                    dict_pincode[pincode].append([])
                    dict_pincode[pincode].append([])
                    dict_pincode[pincode][0].append(email)
                    dict_pincode[pincode][1].append(each.id)
                # check_availabilty_pincode(each)

            elif each.to_dict()['type'] == "2":
                district_id = each.to_dict()['district']
                email = each.to_dict()['email']

                if district_id in dict_district :
                    dict_district[district_id][0].append(email)
                    dict_district[district_id][1].append(each.id)
                else:
                    dict_district[district_id] = list()
                    dict_district[district_id].append([])
                    dict_district[district_id].append([])
                    dict_district[district_id][0].append(email)
                    dict_district[district_id][1].append(each.id)
                # check_availabilty_district(each)



def check_availabilty_pincode():
    from datetime import date
    for pincode, data in dict_pincode.items():
        # today_date = date.today().strftime('%d-%m-%Y')
        to = data[0]
        id_list = data[1]
        pin_obj = SlotAvailableByID(target=pincode, mode = "Pin")
        pin_obj.get_slot_availability()
        flag, index, slots, age, date = pin_obj.return_list[0], pin_obj.return_list[1], pin_obj.return_list[2], pin_obj.return_list[3],pin_obj.return_list[4]
        if flag == True:
            email_obj = Notify(to, index, slots, age, date)
            if email_obj.send_mail():
                remove_from_firebase(id_list, to)

def check_availabilty_district():
    from datetime import date
    for district_id, data in dict_district.items():
        to = data[0]
        id_list = data[1]
        dist_obj = SlotAvailableByID(target=district_id, mode = "District")
        dist_obj.get_slot_availability()
        flag, index, slots, age, date = dist_obj.return_list[0], dist_obj.return_list[1], dist_obj.return_list[2], dist_obj.return_list[3], dist_obj.return_list[4]
        if flag == True:
            email_obj = Notify(to, index, slots, age, date)
            if email_obj.send_mail():
                remove_from_firebase(id_list, to)


def remove_from_firebase(id_list, to):
    url = "https://cowin-realpython.herokuapp.com/update?id="

    for i in range(len(id_list)):
        new_url = url + id_list[i]
        requests.post(new_url)
        print('Removed: \n\tEmail:'+to[i] +' \n\tUID:'+id_list[i]+'\n')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    while True:
        from datetime import date
        test_url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=294&date="
        test_date = date.today().strftime('%d-%m-%Y')
        test_url += test_date

        try:
            test_response = requests.get(test_url, headers={"accept": "application/json", "Accept-Language": "hi_IN",
                                                          "user-agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"}).json()['centers']
            # print("Cowin API Working")
            usersRef = db.collection('cowinUsers')
            testusersRef = db.collection('testcowinUsers')
            users_table = usersRef
            get_endpoint_data(users_table)
            check_availabilty_pincode()
            check_availabilty_district()
            print("5 min break")
            time.sleep(900)
        except:
            print("Cowin API Down")
            print("5 min break")
            time.sleep(900)