# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import requests
import time
# import pandas as pd
from SlotByPin import SlotAvailableByPincode
from SlotByDist import SlotAvailableByDistrict
from Notify import Notify


# df_pincode = pd.DataFrame(columns=['Date', 'Email', 'Pincode'])
# df_district = pd.DataFrame(columns=['Date', 'Email', 'District_id'])
dict_pincode = dict()
dict_district = dict()

def get_endpoint_data():
    # Use a breakpoint in the code line below to debug your script.
    request_api = "https://cowin-realpython.herokuapp.com/list"
    response = requests.get(request_api).json()
    for each in response:
        # print("This is being printed")
        data_dict = dict()
        if bool(each) and each['optin'] == "1":
            if each['type'] == "1":
                pincode = each['pincode']
                email = each['email']
                # data_dict['Date'] = each['date']
                # data_dict['Email'] = each['email']
                # data_dict['Pincode'] = each['pincode']
                # df_pincode = df_pincode.append(data_dict, ignore_index=True)
                if pincode in dict_pincode:
                    dict_pincode[pincode].append(email)
                else:
                    dict_pincode[pincode] = list()
                    dict_pincode[pincode].append(email)
                # check_availabilty_pincode(each)

            elif each['type'] == "2":
                district_id = each['district']
                email = each['email']
                # data_dict['Date'] = each['date']
                # data_dict['Email'] = each['email']
                # data_dict['District'] = each['district']
                # df_district = df_district.append(data_dict, ignore_index=True)
                if district_id in dict_district :
                    dict_district[district_id].append(email)
                else:
                    dict_district[district_id] = list()
                    dict_district[district_id].append(email)
                # check_availabilty_district(each)



def check_availabilty_pincode():
    from datetime import date
    for pincode, emails in dict_pincode.items():
        # today_date = date.today().strftime('%d-%m-%Y')
        to = emails
        pin_obj = SlotAvailableByPincode(pincode=pincode)
        pin_obj.get_slot_availability()
        flag, index, slots, age, date = pin_obj.return_list[0], pin_obj.return_list[1], pin_obj.return_list[2], pin_obj.return_list[3],pin_obj.return_list[4]
        if flag == True:
            Notify(to, index, slots, age, date)

def check_availabilty_district():
    from datetime import date
    for district_id, emails in dict_district.items():
        # today_date = date.today().strftime('%d-%m-%Y')
        to = emails
        dist_obj = SlotAvailableByDistrict(district_id=district_id)
        dist_obj.get_slot_availability()
        flag, index, slots, age, date = dist_obj.return_list[0], dist_obj.return_list[1], dist_obj.return_list[2], dist_obj.return_list[3], dist_obj.return_list[4]
        if flag == True:
            Notify(to, index, slots, age, date)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    while True:
        # print("This is being printed")
        get_endpoint_data()
        check_availabilty_pincode()
        check_availabilty_district()
        time.sleep(300)


