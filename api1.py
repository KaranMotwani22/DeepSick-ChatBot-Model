import requests
import json
import pandas as pd


def call_url(temp):

    emp_id = temp
    url1 = "https://weatworktest.mahyco.com/webapi/api/MyProfile/GetMyProfileData"
    headers1 = {
        "Authorization": "bearer -bEIjdVn7sthgn9NDxcxmdfU4SoOz5JOi6t2Ne3stzR2XTIiP-thQ89MhUGtIXYNXno_xTTUL1MkYt_EqUTaJYUEAFMl9K-AI89i7gNci_jginAw7qZCL2Ba7dxUxZcQHZWJRCQ7FPzxmaScPqxmMm5uyucbVWi6n60BRRYbQgltZWUeMglWSxdOKaLrq2JwyJiA-LgVoIxLP__XGGhVfQ"}
    data1 = {"loginDetails": {
        "LoginEmpID": 97260738,
        "LoginEmpCompanyCodeNo": "4000"
    }
    }

    response1 = requests.post(url1, headers=headers1, json=data1)
    data1 = response1.json()

    dfs = {}
    profile_data = data1.get('ProfileData', [])
    if profile_data:
        first_profile = profile_data[0]
            
            # Create DataFrames for each table in the profile
        for table_name, rows in first_profile.items():
            if isinstance(rows, list):
                dfs[table_name] = pd.DataFrame(rows)
            else:
                print(f"Unexpected format for table {table_name}")


    # second api data
    url2 = "https://weatworktest.mahyco.com/webapi/api/Leave/GetLeaveData"
    headers2 = {
        "Authorization": "bearer -bEIjdVn7sthgn9NDxcxmdfU4SoOz5JOi6t2Ne3stzR2XTIiP-thQ89MhUGtIXYNXno_xTTUL1MkYt_EqUTaJYUEAFMl9K-AI89i7gNci_jginAw7qZCL2Ba7dxUxZcQHZWJRCQ7FPzxmaScPqxmMm5uyucbVWi6n60BRRYbQgltZWUeMglWSxdOKaLrq2JwyJiA-LgVoIxLP__XGGhVfQ"}
    data2 = {"loginDetails": {
        "LoginEmpID": 97260738,
        "LoginEmpCompanyCodeNo": "4000",
        "LoginEmpGroupId": "4000"
    }
    }

    response2 = requests.post(url2, headers=headers2, json=data2)
    data2 = response2.json()
    for table_name, rows in data2.items():
        if isinstance(rows, list):
            dfs[table_name] = pd.DataFrame(rows)
        else:
            print(f"Unexpected format for table {table_name}")

    return dfs

