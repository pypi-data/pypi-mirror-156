import requests
import pandas as pd
class data:
    def fetch(id:str, bbox = [], start_date:str = "", end_date:str = ""):
        api_url = "https://oak.cast.uark.edu/metadata-api/Data/SpaceTimeLookup"
        headers={
            'Content-type':'application/json-patch+json',
            'Accept':'text/plain'
        }
        if start_date == "" or end_date == "":
            request = {"id": id, "bbox": bbox}
        else:
            request ={"id": id,"bbox": bbox,"startDate": start_date, "endDate": end_date}

        response = requests.post(api_url, json=request, headers=headers)
        json_response = response.json()
        code = response.status_code
        df = pd.json_normalize(json_response['data']['features'])
        return df

    #test = fetch(id= "6255d6681a1205e8b86623f0", bbox= [-95.774704, 35.995683, -89.098843, 40.61364], start_date= "8/29/2003 12:00:00 AM", end_date="8/31/2003 12:00:00 AM")
    #test1 = fetch(id= "6255d6681a1205e8b86623f0", start_date= "8/29/2003 12:00:00 AM", end_date="8/31/2003 12:00:00 AM")
    #test2 = fetch(id= "6255d6681a1205e8b86623f0", bbox= [-95.774704, 35.995683, -89.098843, 40.61364])
    #test3 = fetch(id= "6255d6681a1205e8b86623f0", bbox= [-95.774704, 35.995683, -89.098843, 40.61364],start_date= "8/29/2003 12:00:00 AM")
    #test4 = fetch(id= "6255d6681a1205e8b86623f0", bbox= [-95.774704, 35.995683, -89.098843, 40.61364], end_date="8/31/2003 12:00:00 AM")
    #test5 = fetch(id= "6255d6681a1205e8b86623f0")
