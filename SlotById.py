import requests
import datetime
class SlotAvailableByID:

    def __init__(self, target, mode, age='18', date_var=None):
        self.target = target
        self.date_var = date_var
        self.age = age
        self.return_list = list()
        self.mode = mode


    def get_slot_availability(self):
        from datetime import date
        if self.date_var is None:
            self.date_var = date.today()
        else:
            self.date_var = datetime.datetime.strptime(self.date_var, '%Y-%m-%d')

        self.date_var = self.date_var.strftime('%d-%m-%Y')
        base_url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarBy'
        param = "pincode" if self.mode == "Pin" else "district_id"
        request_api = base_url + self.mode+"?"+param+"="+str(self.target)+"&date="+self.date_var
        try:
            response = requests.get(request_api, headers={"accept":"application/json", "Accept-Language": "hi_IN", "user-agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"}).json()['centers']

            for each in response:
                for values in each['sessions']:
                    if values['min_age_limit'] == int(self.age) and values['available_capacity']>0:
                        index = each['name'] + " " + each['state_name'] + " " + each['district_name'] + " " + \
                                str(each['pincode'])
                        slots = values['available_capacity']
                        age = values['min_age_limit']
                        date = values['date']
                        self.return_list.append(True)
                        self.return_list.append(index)
                        self.return_list.append(slots)
                        self.return_list.append(age)
                        self.return_list.append(date)
                        return

            self.return_list.append(False)
            self.return_list.append(0)
            self.return_list.append(0)
            self.return_list.append(0)
            self.return_list.append(0)
            return

        except:
            print("except: Pincode:", self.target)
            self.return_list.append(False)
            self.return_list.append(0)
            self.return_list.append(0)
            self.return_list.append(0)
            self.return_list.append(0)
            return