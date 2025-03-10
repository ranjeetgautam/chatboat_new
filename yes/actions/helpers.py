import requests
import random
import json
from datetime import datetime
import re


def convert_date_format(date_str):
    try:
        # Check if the date is already in yyyy-mm-dd format
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        # If parsing is successful, the format is correct
        return date_str
    except ValueError:
        # If ValueError is raised, the format is different and needs conversion
        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
        new_date_str = date_obj.strftime('%Y-%m-%d')
        return new_date_str


def send_aadhar_otp(aadhar_number, userId, auth_token,user_consent=True):
   # return True, "Otp Send Successfully *******9662,NA"
    print("INPUT: ", aadhar_number, userId,auth_token, user_consent)
    params = {
        'aadharNo': aadhar_number,
        'userId': userId,
        'consent': user_consent
    }
    url = f"http://13.232.66.157:8080/api/auth/aadhar/v1/otp?aadharNo={params['aadharNo']}&consent={params['consent']}&userId={params['userId']}"
    payload = ""
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en',
        'Authorization': 'Bearer '+auth_token,
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'http://13.232.66.157:3000',
        'Referer': 'http://13.232.66.157:3000/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

   # Convert to cURL command

    curl_command = f"curl -X POST '{url}'"
    for key, value in headers.items():
        curl_command += f" -H '{key}: {value}'"

    curl_command += f" -d '{json.dumps(payload)}'"

    print("Equivalent cURL command:")
    print(curl_command)

    print("response", response.json())

    print(response.text)

    if response.status_code == 200:
        response = response.json()
        if response['status'] == 200:
            return True, response['data']

        else:
              return False, response['message']
    try:
        response = response.json()
        return False, response['message']
    except:
        return False, "Failed to send otp."


# def verify_aadhar_otp(aadhar_number, entered_otp, userId,auth_token):
#     status = False
#     print("INPUT for aadhar verifiation", aadhar_number, entered_otp, userId)
#
#     url = f"http://13.232.66.157:8080/api/auth/aadhar/v1/kyc?aadharNo={aadhar_number}&otp={entered_otp}&userId={userId}"
#     payload = {}
#     headers = {
#       'Accept': 'application/json, text/plain, */*',
#       'Accept-Language': 'en',
#       'Authorization': 'Bearer '+auth_token,
#       'Connection': 'keep-alive',
#       'Content-Length': '0',
#       'Content-Type': 'application/x-www-form-urlencoded',
#       'Origin': 'http://13.232.66.157:3000',
#       'Referer': 'http://13.232.66.157:3000/',
#       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
#     }
#
#     response = requests.request("POST", url, headers=headers, data=payload)
#
#     # Convert to cURL command
#
#     curl_command = f"curl -X POST '{url}'"
#     for key, value in headers.items():
#         curl_command += f" -H '{key}: {value}'"
#
#     curl_command += f" -d '{json.dumps(payload)}'"
#
#     print("Equivalent cURL command:")
#     print(curl_command)
#
#     print("response", response.json())
#
#     print(response.text)
#
#     #with open("aadhar_response.json", "w") as json_file:
#     #json.dump(response.json(), json_file)
#     address_keys = {
#         "house": "House",
#         "street": "Street",
#         "vtc": "Village/Town/City",
#         "loc": "Location",
#         "subdist": "Sub-district",
#         "dist": "District",
#         "state": "State",
#         "pc": "Pin Code"
#     }
#     print(response.json(), "AADHAR OTP VERIFICATION RESPONSE")
#     if response.status_code  ==200:
#         response = response.json()
#         print(response, "OTP VERIFICATION RESPONSE")
#         if response["status"] != 200:
#             return False,  response['message'], None
#
#         message = response['message']
#         if message == "Aadhar kyc process completed":
#             status = True
#             gender = response['data']['gender']
#             dob = response['data']['dob']
#             care_of = response['data']['co']
#             pincode = response['data']['pc']
#             relation_with_guardian, guardian = determine_relation(care_of)
#             if gender == 'M':
#                 title = "Mr."
#             elif gender == "F":
#                 title = "Mrs."
#             elif gender == "O":
#                 title = ""
#             else:
#                 title = ""
#
#             name = response['data']['name']
#             address = ""
#             for key, val in address_keys.items():
#                 response_val = response['data'].get(key, '')
#                 if response_val:
#                     address += f"{val}: {response_val}\n"
#             out = {'status': status, 'title': title, 'name': name, 'address': address, 'gender': gender, 'dob': dob,
#                    'guardian': guardian, 'relation_with_guardian': relation_with_guardian, "aadhar_pincode": pincode}
#             return out
#     # return {'status': False, 'title': None, 'name': None, 'address': None, 'gender': None, 'dob': None,
#     #         'guardian': None, 'relation_with_guardian': None, "aadhar_pincode": None}
#     # return False,None, None, None

def verify_aadhar_otp(aadhar_number, entered_otp, userId, auth_token):
    status = False
    print("Input for Aadhar verification:", aadhar_number, entered_otp, userId)

    url = f"http://13.232.66.157:8080/api/auth/aadhar/v1/kyc?aadharNo={aadhar_number}&otp={entered_otp}&userId={userId}"
    payload = {}
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en',
        'Authorization': f'Bearer {auth_token}',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'http://13.232.66.157:3000',
        'Referer': 'http://13.232.66.157:3000/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_data = response.json()
        print("Aadhar OTP Verification Response:", response_data)

        address_keys = {
            "house": "House",
            "street": "Street",
            "vtc": "Village/Town/City",
            "loc": "Location",
            "subdist": "Sub-district",
            "dist": "District",
            "state": "State",
            "pc": "Pin Code"
        }

        # Check if the status is 200 and handle the response
        if response_data.get("status") == 200:
            message = response_data.get('message', '')
            print(message,"............")
            # if message != "Aadhar KYC process completed":
            #     return {'status': True, 'message': message, 'data': None}

            status = True
            data = response_data.get('data', {})
            gender = data.get('gender', '')
            dob = data.get('dob', '')
            care_of = data.get('co', '')
            pincode = data.get('pc', '')
            relation_with_guardian, guardian = determine_relation(care_of)

            # Determine title based on gender
            title = ""
            gender_data = "Other"
            sdw = ""
            if gender == 'M':
                title = "Mr."
                gender_data = 'Male'
                sdw= "SON OF"
            elif gender == "F":
                title = "Mrs."
                gender_data = 'Female'
                sdw = "DAUGHTER OF"

            name = data.get('name', '')
            print(message, "............"+ sdw)
            address = ""
            for key, val in address_keys.items():
                response_val = data.get(key, '')
                if response_val:
                    address += f"{val}: {response_val}\n"

            result = {
                'status': status,
                'title': title,
                'name': name,
                'address': address,
                'gender': gender_data,
                'dob': dob,
                'guardian': guardian,
                'relation_with_guardian': relation_with_guardian,
                'aadhar_pincode': pincode,
                'sdw': sdw
            }
            return result

        else:
            message = response_data.get('message', 'Unknown error occurred.')
            return {'status': False, 'message': message, 'data': None}

    except requests.exceptions.RequestException as e:
        print("HTTP Request Error:", e)
        return {'status': False, 'message': 'Network error occurred.', 'data': None}
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return {'status': False, 'message': 'Invalid response from server.', 'data': None}
    except Exception as e:
        print("Unexpected error:", e)
        return {'status': False, 'message': 'An unexpected error occurred.', 'data': None}

def determine_relation(description):
    relation_map = {
        'S/O': 'Son of',
        'D/O': 'Daughter of'
    }

    parts = description.split(' ', 1)
    if len(parts) != 2:
        return "Invalid description format"

    relation_code, name = parts
    relation = relation_map.get(relation_code.upper(), "Unknown relation code")

    return relation, name


def send_otp_register_and_login(mobile_no):
    # return {
    #     'status': True,
    #     "message":"OTP sent to your mobile no",
    #     'already_registered': True
    # }
    print(f"Input mobile_no : {mobile_no}")
    #url_register = "http://13.232.66.157:8080/api/auth/register_login/send_otp_for_register_and_login"
    url_authenticate = "http://13.232.66.157:8080/api/auth/send_otp"

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'http://13.232.66.157:3000',
        'Referer': 'http://13.232.66.157:3000/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        #'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiI4NzAwMDAwMDAwIiwiZXhwIjoxODA2MzE5OTYxLCJhdXRoIjoiIiwiaWF0IjoxNzE5OTE5OTYxfQ.CRWvRnCWKW9lTYDQrUR59q49MaT47ttM1iiXw5pBUIAwlrjIuSbqJW5UqPjrZ3VTvk6WUbgTcfyMyA5sODJUWA'
    }

    payload_register = json.dumps({
        "authType": "CREATE_FARMER",
        "otpType": "mobile",
        "mobileNo": mobile_no,
        "registrationType":"mobile"
    })

    response = requests.post(url_authenticate, headers=headers, data=payload_register)

    # Convert to cURL command
    curl_command = f"curl -X POST '{url_authenticate}'"
    for key, value in headers.items():
        curl_command += f" -H '{key}: {value}'"

    curl_command += f" -d '{json.dumps(payload_register)}'"

    print("Equivalent cURL command:")
    print(curl_command)

    print("response", response.json())

    if response.status_code != 200:
        print('already registered , sneding logging in otp')
        payload_authenticate = json.dumps({
            "authType": "AUTHENTICATE",
            "otpType": "mobile",
            "mobileNo": mobile_no,
            "registrationType":"mobile"
        })

        response = requests.post(url_authenticate, headers=headers, data=payload_authenticate)
        response.raise_for_status()
        message = response.json()['message']
        already_registered = True  # login
    else:
        response.raise_for_status()
        message = response.json()['message']
        already_registered = False

    status = True if response.ok else False

    return {
        'status': status,
        "message": message,
        'already_registered': already_registered
    }


def verify_phone_otp(mobile_no, otp, already_registered):
    #     response = {
    #     "status": 200,
    #     "message": "Authenticated",
    #     "data": {
    #         "userEmail": None,
    #         "userId": 1138,
    #         "role": "FARMER",
    #         "roleId": 2,
    #         "userName": "9340108470",
    #         "lastLoginList": [
    #             {
    #                 "loginTime": "2024-07-22T12:14:29.038991",
    #                 "loginType": "SUCCESSFUL"
    #             }
    #         ],
    #         "orgnisationId": None,
    #         "farmerRegistered": False,
    #         "admin": False,
    #         "id_token": "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiI5MzQwMTA4NDcwIiwiZXhwIjoxODA4MDQxNzMyLCJhdXRoIjoiIiwiaWF0IjoxNzIxNjQxNzMyfQ.-PoO42_xqw0ZNV0i2tuBbQTFxBYfrGLThtnSWywXik_VqnYCnRoiJ50F69eGRDDAVcIt-u8TpcyBwJi_hHNfXA",
    #         "refresh_token": "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiI5MzQwMTA4NDcwIiwiZXhwIjoxODA4MDQxNzMyLCJhdXRoIjoiIiwiaWF0IjoxNzIxNjQxNzMyfQ.-PoO42_xqw0ZNV0i2tuBbQTFxBYfrGLThtnSWywXik_VqnYCnRoiJ50F69eGRDDAVcIt-u8TpcyBwJi_hHNfXA"
    #     },
    #     "dataList": None
    # }
    #     status =True
    #     message   = response['message']
    #     userId = response['data']['userId']
    #     auth_token = response['data']['id_token']
    #     return {
    #     'status': status,
    #     'message':message,
    #     'userId':userId,
    #     'auth_token':auth_token
    # }
    if not already_registered:  # register
        url = "http://13.232.66.157:8080/api/auth/reg_farmer"
    else:  # 'login'
        url = "http://13.232.66.157:8080/api/auth/login_verify_otp"
    # else:
    #     return {'status': 'fail', 'message': 'Invalid action'}

    payload = json.dumps({
        "authType": "AUTHENTICATE",
        "otpType": "mobile",
        "mobileNo": mobile_no,
        "otp": otp,
        "registrationType":"mobile"
    })

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'http://13.232.66.157:3000',
        'Referer': 'http://13.232.66.157:3000/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        #'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiI4NzAwMDAwMDAwIiwiZXhwIjoxODA2MzE5OTYxLCJhdXRoIjoiIiwiaWF0IjoxNzE5OTE5OTYxfQ.CRWvRnCWKW9lTYDQrUR59q49MaT47ttM1iiXw5pBUIAwlrjIuSbqJW5UqPjrZ3VTvk6WUbgTcfyMyA5sODJUWA'
    }

    response = requests.post(url, headers=headers, data=payload)
    # response.raise_for_status()
    print(response.json(), 'response for otp verification')
    if response.status_code == 200:
        status = True
        response = response.json()
        message = response['message']
        userId = response['data']['userId']
        auth_token = response['data']['id_token']
        return {
            'status': status,
            'message': message,
            'userId': userId,
            'auth_token': auth_token
        }

    else:
        message = response.json()['message']
        status = False
        return {
            'status': status,
            'message': message
        }


# Function to load mappings from JSON file
def load_mapping():
    with open('./actions/mapping.json', 'r') as file:
        mapping = json.load(file)
    print('loaded mapping', mapping)
    return mapping


def get_user_by_id(userId: str, auth_token: str):
    print(f"User Id {userId} || Bearer Token {auth_token}")
    url = f"http://13.232.66.157:8080/api/party/farmer/get_by_id?userId={userId}"
    payload = {}
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en',
        'Authorization': f'Bearer {auth_token}',
        'Connection': 'keep-alive',
        'Origin': 'http://13.232.66.157:3000',
        'Referer': 'http://13.232.66.157:3000/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.status_code)
    # print(response.text)
    if response.status_code != 401:
        response = response.json()
        return response
    else:
        return "Unauthorized"


def get_farmer_id(userId: str, auth_token: str):
    response = get_user_by_id(userId, auth_token)
    if response == 'Unauthorized':
        return None
    # print(response, 'farmer id response')
    if response['status'] == 200:
        if response['data']:
            return response['data']['farmerId']
    return None


def save_nominee_details(tracker):
    # Read the mapping file
    mapping = load_mapping()
    print('mapping file data', mapping)
    userId = tracker.get_slot('userId')
    auth_token = tracker.get_slot('auth_token')

    # get farmer id
    farmerId = get_farmer_id(userId=userId, auth_token=auth_token)

    print('userId ...... ', userId)
    print('farmerId ...... ', farmerId)
    # Retrieve slot values from tracker
    nominee_details = {
        "nomineeName": tracker.get_slot("nominee_name"),
        "nomineeAge": tracker.get_slot("nominee_age"),
        "annualIncome": "",
        "gender": tracker.get_slot("nominee_gender"),
        "relationship": tracker.get_slot("relationship_with_nominee"),
        "occupation": tracker.get_slot("nominee_occupation")
    }
    print('nominee details', nominee_details)

    # Map nominee details to IDs
    mapped_details = {
        "nomineeName": nominee_details.get("nomineeName"),
        "nomineeAge": nominee_details.get("nomineeAge"),
        "annualIncome": nominee_details.get("annualIncome"),
        "genderId": mapping["gender"][nominee_details.get("gender").lower()],
        "nomineeRelationId": mapping["relationship"][nominee_details.get("relationship").lower()],
        "nomineeOccupationId": mapping["occupation"][nominee_details.get("occupation").lower()]
    }

    # Prepare the data to be sent
    data = json.dumps([mapped_details])
    # auth_token="eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiI2NTAwMDAwMTAxIiwiZXhwIjoxODA3NDM4MTY5LCJhdXRoIjoiIiwiaWF0IjoxNzIxMDM4MTY5fQ.ApAXUrEEkMwfpbiI4nz7IoGvIKxPMWTnNE8b0pYIeVIkMZ101eobDU21ruICyoF1DGfJM4QpZiJIMHbil6dDug"

    # Define the URL and headers
    url = f'http://13.232.66.157:8080/api/party/farmer/save_nominee_detail/{farmerId}'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en',
        'Authorization': f'Bearer {auth_token}',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'http://13.232.66.157:3000',
        'Referer': 'http://13.232.66.157:3000/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    # Send the POST request
    # print(f"Headers: {headers} Data: {data}")

    response = requests.post(url, headers=headers, data=data, verify=False)
    print(response.status_code)
    print(response.text)
    # Print the response
    print('Nominee response', response.json())
    return response.json()

def save_address_details(tracker):
    # Read the mapping file
    mapping = load_mapping()
    print('mapping file data', mapping)
    userId = tracker.get_slot('userId')
    auth_token = tracker.get_slot('auth_token')
    print('userId ...... ', userId)

    # Retrieve slot values from tracker
    address_details = {
        "presentAddress1": tracker.get_slot("present_address_1"),
        "presentState": tracker.get_slot("present_state"),
        "presentDistrict": tracker.get_slot("present_district"),
        "presentPincode": tracker.get_slot("present_pincode"),
        "permanentAddress1": tracker.get_slot("permanent_address_1"),
        "permanentState": tracker.get_slot("permanent_state")   ,
        "permanentDistrict": tracker.get_slot("permanent_district"),
        "permanentPincode": tracker.get_slot("permanent_pincode")
    }
    print('address_details', address_details)

    # Prepare the data to be sent
    # data = json.dumps([mapped_details])
    data =[
        {
            # "id": 23,
             "stateName": address_details["presentState"],
             "districtName": address_details["presentDistrict"],
             "address": address_details["presentAddress1"],
             "pincode": address_details["presentPincode"],
             "addressType": "CURRENT_ADDRESS"
        },
        {
            # "id": 24,
            "stateName": address_details["permanentState"],
            "districtName": address_details["permanentDistrict"],
            "address": address_details["permanentAddress1"],
            "pincode": address_details["permanentPincode"],
            "addressType": "PERMANENT_ADDRESS"

        }
    ]

    # Define the URL and headers
    url = f'http://13.232.66.157:8080/api/party/farmer/bot/save_address?userId={userId}&bothAddressSame=false'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en',
        'Authorization': f'Bearer {auth_token}',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'http://13.232.66.157:3000',
        'Referer': 'http://13.232.66.157:3000/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    # Send the POST request
    print(f"Headers: {headers} Data: {data}  url: {url}")

    # Convert to cURL command
    curl_command = f"curl -X POST '{url}'"
    for key, value in headers.items():
        curl_command += f" -H '{key}: {value}'"

    curl_command += f" -d '{json.dumps(data)}'"

    print("Equivalent cURL command:")
    print(curl_command)

    response = requests.post(url, headers=headers, data=data, verify=False)

    print(response.status_code)
    print(response.text)
    # Print the response
    print('address_details response', response.json())
    return response.json()


# Function to save user profile using API
def save_user_profile(tracker):
    userId = tracker.get_slot('userId')
    print("userId.......", userId)
    url = f'http://13.232.66.157:8080/api/party/farmer/save_user_profile?farmerId=&userId={userId}'
    auth_token = tracker.get_slot('auth_token')
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en',
        'Authorization': f'Bearer {auth_token}',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'http://13.232.66.157:3000',
        'Referer': 'http://13.232.66.157:3000/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    mapping = load_mapping()

    # Mapping keys from JSON file
    title_mapping = mapping.get("title", {})
    id_proof_mapping = mapping.get("id_proof", {})
    caste_mapping = mapping.get("caste", {})
    occupation_mapping = mapping.get("occupation", {})
    religion_mapping = mapping.get("religion", {})
    gender_mapping = mapping.get("gender", {})
    relationship_mapping = mapping.get("relationship", {})
    print("....."+tracker.get_slot("user_title")+"..."+tracker.get_slot("user_gender"))


    # Constructing data payload
    data = {
        "currentAddress": "",
        "registerId": "",
        "associateRegisterId": "",
        "permanentAddress": tracker.get_slot("permanent_address"),  # newly added
        "titleId": 380,#title_mapping.get(tracker.get_slot("user_title").lower(), ""),
        "genderId": 44,#gender_mapping.get(tracker.get_slot("user_gender").lower(), ""),
        "religionId": religion_mapping.get(tracker.get_slot("user_religion").lower(), ""),
        "casteId": caste_mapping.get(tracker.get_slot("caste").lower(), ""),
        "occupationId": occupation_mapping.get(tracker.get_slot("user_occupation").lower(), ""),
        "physicallyHandicapped": "Yes" if tracker.get_slot("has_disability") else "No",
        "fullName": tracker.get_slot("user_name"),
        "relativeName": tracker.get_slot("guardian"),
        "dateOfBirth": convert_date_format(tracker.get_slot("user_dob")),
        "aadhaarNo": tracker.get_slot("aadhar_number"),
        "idProofNo": tracker.get_slot("id_number"),
        "pacsMemberNumber": None,
        "isPacsMember": 0,
        "createdBy": "self",
        "createdOn": "",
        "modifiedOn": "",
        "aadhaarAddress": tracker.get_slot("aadhar_address"),  # newly added
        "aadhaarPincode": tracker.get_slot("aadhar_pincode"),  # newly added,
        "sdwOf": tracker.get_slot("sdw"),
        "asAboveAddress": "",
        "email": "",
        "mobileNo": tracker.get_slot("phoneNumber"),
        "isSameAsPermanentAddress": False,
        "mobileNumber": tracker.get_slot("phoneNumber"),
        "proofOfIdentityId": id_proof_mapping.get(tracker.get_slot("id_type").lower(), "")
    }
    print(" Data...:",data)
    response = requests.post(url, headers=headers, json=data, verify=False)
    print(f"Headers: {headers} Data: {data}")
    print(response.status_code)
    # print(response.text)
    print(response.json())
    return response.json()


def structure_existing_details(response):
    field_labels = {
        "farmerId": "Farmer ID",
        "fullName": "Full Name",
        "castName": "Caste",
        "genderName": "Gender",
        "proofOfIdentityName": "Proof of Identity",
        "idProofNumber": "ID Proof Number",
        "physicallyChallenged": "Physically Challenged",
        "mobileNo": "Mobile Number",
        "aadharAddress": "Aadhar Address",
        "relativeName": "Relative Name"
    }
    details = ""
    if 'data' not in response:
        return details
    for label, display_label in field_labels.items():
        value = response['data'].get(label, '')
        details += f"{display_label}: {value}\n"
    return details.strip()


def get_phone_from_sender_id(sender_id):
    if len(sender_id) > 10 and sender_id.startswith('91'):
        return sender_id[2:]
    return sender_id


def extract_aadhar_number(aadhar_number: str) -> (bool, str):
    try:
        pattern = re.compile(r'\b(\d{12})\b|\b(\d{4}\s\d{4}\s\d{4})\b', re.IGNORECASE)
        match = pattern.search(aadhar_number)
        if match:
            return True, match.group(0).replace(" ", "")
        else:
            return False, ""
    except Exception as e:
        print(f"Exception: {e}")
        print(f"Error occurred: {e}")
        return False, ""


def extract_phone_number(text):
    # Define the regex pattern for a 10-digit phone number
    pattern = r'\b\d{10}\b'
    # Search for the pattern in the text
    match = re.search(pattern, text)
    # If a match is found, return the phone number
    if match:
        return True, match.group(0)
    else:
        return False, None


def extract_otp(otp: str) -> (bool, str):
    try:
        pattern = re.compile(r'\b(\d{6})\b', re.IGNORECASE)
        match = pattern.search(otp)
        if match:
            extracted_otp = match.group(0)
            return True, extracted_otp
        else:
            return False, ""
    except Exception as e:
        print(f"Exception: {e}")
        print(f"Error occurred: {e}")
        return False, ""


def is_valid_pan_number(pan_number: str) -> bool:
    pattern = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')
    return bool(pattern.match(pan_number))


def clean_name(name):
    return "".join([c for c in name if c.isalpha()])


id_type_regex = {
    "drivinglicense": r'^[A-Z]{2}\d{13}$',
    "mgnregacard": r'^[A-Z0-9]{10}$',
    "pancard": r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$',
    "passport": r'^[A-PR-WY][1-9]\d\s?\d{4}[1-9]$',
    "voterid": r'^[A-Z]{3}[0-9]{7}$'
}


def is_valid_id_number(id_type: str, id_number: str) -> bool:
    id_type_lower = id_type.lower().replace(" ", "")
    if id_type_lower in id_type_regex:
        return bool(re.match(id_type_regex[id_type_lower], id_number))
    return False