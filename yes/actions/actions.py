from typing import Text, List, Any, Dict
from rasa_sdk.events import EventType
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
from rasa_sdk import Tracker
import re
from rasa_sdk.events import AllSlotsReset, FollowupAction, UserUttered, ActiveLoop
from .helpers import *

acceptable_fields_to_change = {
    "phone_number": "Phone Number",
    "id_type": "ID Type",
    "id_number": "ID Number",
    "aadhar_number": "Aadhar Number",
    "user_religion": "Religion",
    "caste": "Caste",
    "has_disability": "Disability",
    "nominee_name": "Nominee Name",
    "nominee_gender": "Nominee Gender",
    "nominee_age": "Nominee Age",
    "nominee_occupation": "Nominee Occupation",
    "nominee_annual_income": "Nominee Income",
    "present_address": "Present Address",
    "permanent_address": "Permanent Address"
}

options_dict = {
    "id_type": [
        "Driving License", "MGNREGA Card", "Pan Card", "Passport", "Voter ID"
    ],
    "caste": [
        "General", "SC", "ST", "OBC"
    ],
    "address_type": [
        "permanent_address", "present_address", "both"
    ],
    "gender": [
        "Male", "Female", "Others"
    ],
    "relationship": [
        "Daughter", "Mother", "Sister", "Wife", "Brother", "Father", "Husband", "Son"
    ],
    "occupation": [
        "Agriculture", "Labourer", "Service"
    ],
    "religion": [
        "Hindu", "Muslim", "Sikh", "Jain", "Christian", "Buddhist", "Parsi", "Zoroastrian", "Other Minorities"
    ]
}


def lower_replace(s):
    s = str(s)
    return s.lower().replace(" ", "")


def print_all_slots(tracker):
    slot_values = tracker.current_slot_values()

    # Print the slot names and values
    for slot_name, slot_value in slot_values.items():
        print(f"Slot '{slot_name}' has value '{slot_value}'")


#
class ActionResetAllSlots(Action):
    def name(self):
        return "action_reset_all_slots"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(
            text="All your entries in this session have been reset, You can start a new conversation now by sending 'Hi'.")
        print("resetting all slots")
        return [AllSlotsReset()]


class ValidatePhoneNumberForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_phoneNumberForm"

    # def validate_useWhatsappNum(
    #         self,
    #         slot_value: Any,
    #         dispatcher: CollectingDispatcher,
    #         tracker: Tracker,
    #         domain: DomainDict,
    # ) -> Dict[Text, Any]:
    #
    #     none_response = {"useWhatsappNum": None, 'retry_phoneNumberForm': 0}
    #     try:
    #         key_to_exclude = 'whatsapp number'
    #         exists = any(slot_value in options for k, options in options_dict.items() if k != key_to_exclude)
    #         if exists:
    #             retry = tracker.get_slot('retry_phoneNumberForm')
    #             print(f'retry value: {retry}')
    #             dispatcher.utter_message(text="Please select from the options mentioned for {key_to_exclude} only.")
    #             return {"useWhatsappNum": None, 'retry_phoneNumberForm': retry + 1}
    #
    #         if slot_value == False:
    #             return {"useWhatsappNum": False}
    #         phoneNumber = get_phone_from_sender_id(tracker.sender_id)
    #         out = self.handle_phoneNumber(dispatcher, phoneNumber)
    #         print('output from otp sender', out)
    #         print(f"Returning Phone Number", phoneNumber)
    #         return {"useWhatsappNum": True, "phoneNumber": phoneNumber, 'already_registered': out['already_registered'],
    #                 'retry_phoneNumberForm': 0}
    #
    #     except Exception as e:
    #         print(f"Exception: {e}")
    #         retry = tracker.get_slot('retry_phoneNumberForm')
    #         print(f'retry value: {retry}')
    #         dispatcher.utter_message(text="An error occurred while validating WhatsApp number usage.")
    #         return {"useWhatsappNum": None, 'retry_phoneNumberForm': retry + 1}

    def handle_phoneNumber(self, dispatcher, slot_value):
        is_phone_number, extracted_phone_number = extract_phone_number(slot_value)
        if not is_phone_number:
            dispatcher.utter_message(text="The phone number is invalid. It should be a 10-digit number.")
            return {"phoneNumber": None, 'already_registered': None}
        extracted_phone_number = int(extracted_phone_number)
        print('extracted phone number', extracted_phone_number)

        out = send_otp_register_and_login(extracted_phone_number)
        print('output from send otp', out)
        message = out.get('message', '')
        already_registered = out.get('already_registered', "")

        if message:
            dispatcher.utter_message(text=message)

        if out['status']:
            return {"phoneNumber": extracted_phone_number, 'already_registered': already_registered,
                    'retry_phoneNumberForm': 0}
        else:
            return {"phoneNumber": None, 'already_registered': None, 'retry_phoneNumberForm': 0}

    def validate_phoneNumber(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        try:
            key_to_exclude = 'phone number'
            exists = any(slot_value in options for k, options in options_dict.items() if k != key_to_exclude)
            if exists:
                retry = tracker.get_slot('retry_phoneNumberForm')
                print(f'retry value: {retry}')
                dispatcher.utter_message(
                    text="Please enter the {key_to_exclude}. Other entries are not allowed at this time.")
                return {"phoneNumber": None, 'already_registered': None, 'retry_phoneNumberForm': retry + 1}

            print(f"phonenumber slot, {slot_value}")
            return self.handle_phoneNumber(dispatcher, slot_value)

        except Exception as e:
            print(f"Exception: {e}")
            retry = tracker.get_slot('retry_phoneNumberForm')
            print(f'retry value: {retry}')
            # if retry==2:
            #     return [UserUttered(text="/restart"),SlotSet("phoneNumber",None)]
            dispatcher.utter_message(text="An error occurred while validating the phone number.")
            return {"phoneNumber": None, 'already_registered': None, 'retry_phoneNumberForm': retry + 1}

    def validate_phone_verification_otp(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        none_response = {
            "phone_verification_otp": None,
            'already_submitted': None,
            'existing_details': None,
            'userId': None,
            'auth_token': None,
            'retry_phoneNumberForm': 0
        }

        try:
            key_to_exclude = 'phone verification otp'
            exists = any(slot_value in options for k, options in options_dict.items() if k != key_to_exclude)
            if exists:
                retry = tracker.get_slot('retry_phoneNumberForm')
                print(f"retry value: {retry}")
                dispatcher.utter_message(
                    text=f"Please enter the {key_to_exclude}. Other entries are not allowed at this time."
                )
                none_response['retry_phoneNumberForm'] = retry + 1
                return none_response

            phoneNumber = tracker.get_slot('phoneNumber')
            print(f"phoneNumber... {phoneNumber}")  # Corrected this line

            if slot_value == '!resendotp':
                out = send_otp_register_and_login(phoneNumber)
                message = out.get('message', '')
                already_registered = out.get('already_registered', "")

                if message:
                    dispatcher.utter_message(text=message)

                if out['status']:
                    return {
                        "phone_verification_otp": None,
                        "phoneNumber": phoneNumber,
                        'already_registered': already_registered,
                        'retry_phoneNumberForm': 0
                    }
                else:
                    return {
                        "phone_verification_otp": None,
                        "phoneNumber": None,
                        'userId': None,
                        'already_registered': None,
                        'retry_phoneNumberForm': 0
                    }

            is_otp, otp_value = extract_otp(slot_value)

            if not is_otp:
                dispatcher.utter_message(text="The OTP is invalid. It should be a 6-digit number.")
                return none_response

            else:
                already_registered = tracker.get_slot('already_registered')
                print(f"Already registered: {already_registered}")
                out = verify_phone_otp(phoneNumber, otp_value, already_registered)
                print(out, 'output from phone helper')

                if out['status']:
                    # Validating if already registered
                    response = get_user_by_id(userId=out['userId'], auth_token=out['auth_token'])

                    if response['status'] == 200 and response['data']:
                        already_submitted = True
                        existing_details = structure_existing_details(response)
                    else:
                        already_submitted = False
                        existing_details = None
                    print(slot_value)
                    return {
                        "phone_verification_otp": slot_value,
                        'already_submitted': already_submitted,
                        'existing_details': existing_details,
                        'userId': out['userId'],
                        'auth_token': out['auth_token'],
                        'retry_phoneNumberForm': 0
                    }
                else:
                    message = out.get('message', '')
                    if message:
                        dispatcher.utter_message(text=message)
                    return none_response

        except Exception as e:
            print(f"Exception: {e}")
            retry = tracker.get_slot('retry_phoneNumberForm')
            print(f"retry value: {retry}")
            dispatcher.utter_message(text="An error occurred while validating the OTP.")
            none_response['retry_phoneNumberForm'] = retry + 1
            return none_response


class ValidateOnboardingForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_onboardingForm"

    def validate_aadhar_number(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        print_all_slots(tracker)
        try:
            key_to_exclude = 'aadhar number'
            exists = any(slot_value in options for k, options in options_dict.items() if k != key_to_exclude)
            if exists:
                retry = tracker.get_slot('retry_onboardingForm')
                print(f'retry value: {retry}')
                dispatcher.utter_message(
                    text="Please enter the {key_to_exclude}. Other entries are not allowed at this time.")
                return {"aadhar_number": None, 'retry_onboardingForm': retry + 1, "aadhar_verification_otp": None}

            is_aadhar_number, extracted_aadhar_number = extract_aadhar_number(slot_value)
            if not is_aadhar_number:
                dispatcher.utter_message(
                    text="The Aadhaar number is invalid. It should be a 12-digit number in format 1234 5678 1234")

                return {"aadhar_number": None, 'retry_onboardingForm': 0, "aadhar_verification_otp": None}

            extracted_aadhar_number = int(extracted_aadhar_number)
            userId = tracker.get_slot('userId')
            auth_token = tracker.get_slot('auth_token')  # Retrieve the token
            print("auth_token.........."+auth_token)
            status, message = send_aadhar_otp(aadhar_number=extracted_aadhar_number, userId=userId, user_consent=True,auth_token =auth_token)

            if status:
                dispatcher.utter_message(text=message)
                return {"aadhar_number": extracted_aadhar_number, 'retry_onboardingForm': 0,
                        "aadhar_verification_otp": None}
            else:
                dispatcher.utter_message(text=message)

                return {"aadhar_number": None, 'retry_onboardingForm': 0, "aadhar_verification_otp": None}

        except Exception as e:
            print(f"Exception: {e}")
            dispatcher.utter_message(text="An error occurred while validating the Aadhaar number.")
            retry = tracker.get_slot('retry_onboardingForm')
            print(f'retry value: {retry}')
            return {"aadhar_number": None, 'retry_onboardingForm': retry + 1, "aadhar_verification_otp": None}

    def validate_aadhar_verification_otp(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        print_all_slots(tracker)
        try:
            key_to_exclude = 'aadhar otp'
            exists = any(slot_value in options for k, options in options_dict.items() if k != key_to_exclude)
            if exists:
                retry = tracker.get_slot('retry_omboardingForm')
                print(f'retry value: {retry}')
                dispatcher.utter_message(
                    text="Please enter the {key_to_exclude}. Other entries are not allowed at this time.")
                retry = tracker.get_slot('retry_onboardingForm')
                print(f'retry value: {retry}')
                return {"aadhar_verification_otp": None, "user_name": None, "aadhar_address": None, "user_title": None,
                        'user_gender': None, 'user_dob': None, 'user_occupation': None, 'guardian': None,
                        'relation_with_guardian': None, 'aadhar_pincode': None, 'retry_onboardingForm': retry + 1}

            aadhar_number = tracker.get_slot('aadhar_number')
            userId = tracker.get_slot('userId')
            user_occupation = 'agriculture'
            auth_token = tracker.get_slot('auth_token')
            print(auth_token)
            if slot_value == '!resendotp':
                status, message = send_aadhar_otp(aadhar_number=aadhar_number, userId=userId, user_consent=True,auth_token =auth_token)
                if status:
                    dispatcher.utter_message(text=message)
                    return {"aadhar_verification_otp": None, "user_name": None, "aadhar_address": None,
                            "user_title": None, 'user_gender': None, 'user_dob': None, 'user_occupation': None,
                            'guardian': None, 'relation_with_guardian': None, 'aadhar_pincode': None}

            is_otp, otp_value = extract_otp(slot_value)

            if not is_otp:
                dispatcher.utter_message(text="The OTP is invalid. It should be a 6-digit number.")

                return {"aadhar_verification_otp": None, "user_name": None, "aadhar_address": None, "user_title": None,
                        'user_gender': None, 'user_dob': None, 'user_occupation': None, 'guardian': None,
                        'relation_with_guardian': None, 'aadhar_pincode': None}

            else:
                out = verify_aadhar_otp(aadhar_number, otp_value, userId,auth_token =auth_token)
                print(out, 'received response from aadhar verification')
                status, title, name, address, gender, dob, guardian, relation_with_guardian, sdw, aadhar_pincode = (
                    out['status'], out['title'], out['name'], out['address'], out['gender'], out['dob'], out['guardian'],
                out['sdw'],out['sdw'], out['aadhar_pincode'])

                if status:
                    if title:
                        dispatcher.utter_message(text=f"Hello {title} {name}! Let's move on to the next steps.")
                    else:
                        dispatcher.utter_message(text=f"Hello {name}! Let's move on to the next steps.")

                    print("sdw:", sdw)

                    return {"aadhar_verification_otp": slot_value,
                            "user_name": name,
                            "aadhar_address": address,
                            'user_title': title,
                            'user_gender': gender,
                            'user_dob': dob,
                            'user_occupation': user_occupation,
                            'guardian': guardian,
                            'relation_with_guardian': relation_with_guardian,
                            'sdw' : sdw ,
                            'aadhar_pincode': aadhar_pincode }

                else:
                    dispatcher.utter_message(text="The OTP is invalid. Please enter correct otp.")
                    return {"aadhar_verification_otp": None, "user_name": None, "aadhar_address": None,
                            "user_title": None, 'user_gender': None, 'user_dob': None, 'user_occupation': None,
                            'guardian': None, 'relation_with_guardian': None, 'aadhar_pincode': None}

        except Exception as e:
            print(f"Exception: {e}")
            dispatcher.utter_message(text="An error occurred while validating the Aadhaar OTP.")
            retry = tracker.get_slot('retry_onboardingForm')
            print(f'retry value: {retry}')
            return {"aadhar_verification_otp": None, "user_name": None, "aadhar_address": None, "user_title": None,
                    'user_gender': None, 'user_dob': None, 'user_occupation': None, 'guardian': None,
                    'relation_with_guardian': None, 'aadhar_pincode': None, 'retry_onboardingForm': retry + 1}

    def validate_id_type(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        print_all_slots(tracker)
        try:
            acceptable_id_types = {
                "drivinglicense": "Driving License",
                "mgnregacard": "MGNREGA Card",
                "pancard": "Pan Card",
                "passport": "Passport",
                "voterid": "Voter ID"
            }
            slot_value = lower_replace(slot_value)
            if slot_value in acceptable_id_types:
                return {"id_type": acceptable_id_types[slot_value], "id_number": None}

        except Exception as e:
            print(f"Exception: {e}")
            dispatcher.utter_message(text="An error occurred while validating the ID type.")
            return {"id_type": None, "id_number": None}

    def validate_id_number(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        print_all_slots(tracker)
        try:
            id_type = tracker.get_slot("id_type")

            if not id_type or not slot_value:
                dispatcher.utter_message(text="Please provide both ID type and ID number.")

                return {"id_number": None}

            if not is_valid_id_number(id_type, slot_value) or slot_value == 'N/A':
                dispatcher.utter_message(
                    text=f"The {id_type} number is invalid. Please provide a valid {id_type} number.")
                return {"id_number": None}

            return {"id_number": slot_value}

        except Exception as e:
            print(f"Exception: {e}")
            dispatcher.utter_message(text="An error occurred while validating the ID number.")

            return {"id_number": None}

    def validate_address_type(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        try:
            if 'permanent' in slot_value.lower():
                return {"address_type": "Permanent", 'address_type2': "Present",
                        "permanent_address": tracker.get_slot('aadhar_address')}

            elif 'present' in slot_value.lower():
                return {"address_type": "Present", 'address_type2': "Permanent",
                        "present_address": tracker.get_slot('aadhar_address')}

            elif 'both' in slot_value.lower():
                return {"address_type": "Both", "address": tracker.get_slot('aadhar_address'),
                        "present_address": tracker.get_slot('aadhar_address'),
                        "permanent_address": tracker.get_slot('aadhar_address')}

        except Exception as e:
            print(f"Exception: {e}")
            dispatcher.utter_message(text="An error occurred while validating the address type.")

            return {"address_type": None}

    def validate_address(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        try:
            address_type2 = tracker.get_slot('address_type2')

            if 'present' in address_type2.lower():
                return {"present_address": slot_value, 'address': slot_value}

            else:
                return {"permanent_address": slot_value, 'address': slot_value}

        except Exception as e:
            print(f"Exception: {e}")
            dispatcher.utter_message(text="An error occurred while validating the address.")

            return {"address": None}

    def validate_has_disability(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        try:
            if slot_value == False:
                return {"has_disability": "No"}

            return {"has_disability": "Yes"}

        except Exception as e:
            print(f"Exception: {e}")
            dispatcher.utter_message(text="An error occurred while validating disability information.")

            return {"has_disability": None}

    def validate_add_nominee(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        try:
            if slot_value == False:
                return {"add_nominee": False, 'nominee_name': "N/A", "relationship_with_nominee": "N/A",
                        "nominee_gender": "N/A", "nominee_annual_income": 0, "nominee_title": 'N/A', "nominee_age": 0,
                        "nominee_occupation": 0}

            return {"add_nominee": True}

        except Exception as e:
            print(f"Exception: {e}")
            dispatcher.utter_message(text="An error occurred while validating nominee information.")

            return {"add_nominee": None}

    def validate_nominee_age(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        try:
            if isinstance(slot_value, str):
                match = re.search(r'\b\d+\b', slot_value)

                if match:
                    age = int(match.group())

                    if age >= 0:
                        return {"nominee_age": age}

            dispatcher.utter_message(text="Please provide a valid age.")

            return {"nominee_age": None}

        except Exception as e:
            print(f"Exception: {e}")
            dispatcher.utter_message(text="An error occurred while validating nominee age.")

            return {"nominee_age": None}

    def parse_income(self, text: str) -> float:
        # Remove any non-numeric characters except for the decimal point
        numeric_text = re.sub(r'[^\d.,]', '', text)

        # Replace common number formats
        numeric_text = numeric_text.replace(',', '')  # Remove commas
        numeric_text = numeric_text.replace('lakh', '00000')  # Convert "lakh" to "00000"
        numeric_text = numeric_text.replace('crore', '00000000')  # Convert "crore" to "00000000"

        try:
            return float(numeric_text)
        except ValueError:
            return None

    def validate_relationship_with_nominee(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        # Mapping between relationship, gender, and title
        print_all_slots(tracker)
        relationship_to_gender_and_title = {
            "Mother": ("Female", "Mrs."),
            "Sister": ("Female", "Miss"),
            "Wife": ("Female", "Mrs."),
            "Daughter": ("Female", "Miss"),
            "Father": ("Male", "Mr."),
            "Brother": ("Male", "Mr."),
            "Husband": ("Male", "Mr."),
            "Son": ("Male", "Mr."),  # "Master" is used as a title for boys, though "Mr." is also common
            "Others": ("Others", "Other")  # Use "Other" for non-binary or unspecified titles
        }

        # Validate the slot value (relationship)
        if slot_value in relationship_to_gender_and_title:
            gender, title = relationship_to_gender_and_title[slot_value]
            # Set the gender and title slots automatically based on the relationship
            return {
                "relationship_with_nominee": slot_value,
                "nominee_gender": gender,
                "nominee_title": title
            }
        else:
            dispatcher.utter_message(text="Invalid relationship. Please select a valid relationship.")
            return {
                "relationship_with_nominee": None,
                "nominee_gender": None,
                "nominee_title": None
            }

    def validate_nominee_annual_income(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        print_all_slots(tracker)
        # Extract numeric value from the slot value text
        income = self.parse_income(str(slot_value))
        print(f"Income:{income}")
        if income is None:
            dispatcher.utter_message(
                text="Invalid income format. Please provide a numeric value or a properly formatted text.")
            return {"nominee_annual_income": None}  # Prompt user to re-enter
        elif income < 0:
            dispatcher.utter_message(text="Income cannot be negative. Please enter a valid amount.")
            return {"nominee_annual_income": None}  # Prompt user to re-enter
        else:
            # The income value is valid
            return {"nominee_annual_income": income}

    def validate_confirmation(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        # Extract numeric value from the slot value text
        if slot_value.lower().strip() == 'confirm':
            return {'confirmation': 'confirm', 'field_to_change': 'NA'}
        elif slot_value.lower().strip() == 'change':
            return {'confirmation': 'change', 'field_to_change': None}
        else:
            return {'confirmation': None}

    def validate_field_to_change(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        acceptable_fields_to_change = ['aadhar_number', 'id_type', 'id_number', "nominee_name", ]
        # Extract numeric value from the slot value text
        if lower_replace(slot_value) in acceptable_fields_to_change:
            return {'field_to_change': 'slot_value', lower_replace(slot_value): None, 'confirmation': None}

        return {'field_to_change': None}


class ActionStopForm(Action):
    def name(self) -> Text:
        return "action_stop_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text="All your entries in this session have been reset, You can start a new conversation now by sending 'Hi'.")

        dispatcher.utter_message(response="utter_form_stopped")
        return [AllSlotsReset(), SlotSet("quit_form", True)]


class AskForSlotAction(Action):
    def name(self) -> Text:
        return "action_ask_phoneNumberForm_useWhatsappNum"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        sender_id = get_phone_from_sender_id(tracker.sender_id)
        phoneNumber = tracker.get_slot('phoneNumber')
        print(f"phone no: {phoneNumber}")
        print(f"Sender ID: {sender_id}")
        dispatcher.utter_message(
            text=f"Do you want to register with this phone number - {phoneNumber}?",
            buttons=[
                {"title": "Yes", "payload": "/affirm"},
                {"title": "No", "payload": "/deny"}
            ]
        )

        return []


class SaveDetails(Action):
    def name(self) -> Text:
        return "action_save_details"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        add_nominee = tracker.get_slot('add_nominee')
        print(".......",tracker)
        print(".......", add_nominee)

        sdw = tracker.get_slot('sdw')
        print("sdw .......", sdw)

        aadhar_response = save_user_profile(tracker)
        dispatcher.utter_message(text=aadhar_response['message'])

        if add_nominee:
            nominee_response = save_nominee_details(tracker)
            # dispatcher.utter_message(text=nominee_response['message'])
            dispatcher.utter_message(text=nominee_response['data'])
            return []


class TriggerForm(Action):
    def name(self) -> Text:
        return "action_trigger_form"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        already_submitted = tracker.get_slot('already_submitted')
        existing_details = tracker.get_slot('existing_details')
        intent = tracker.latest_message['intent'].get('name')
        print(intent, 'latest intent')
        if intent == 'reset':
            dispatcher.utter_message(text="Stopping the form.")
            return [ActiveLoop(None), AllSlotsReset()]
        if not already_submitted:
            return [FollowupAction("onboardingForm")]
        else:
            dispatcher.utter_message(text="Oh! It seems you are already registered. ")
            dispatcher.utter_message(text=f"I have the following details about you, \n {existing_details}")
            dispatcher.utter_message(
                text="You can login to portal (http://13.232.66.157:3000/) to apply for a loan and edit your details further.")
            # return [FollowupAction("utter_already_registered")]


class UserRestart(Action):
    def name(self) -> Text:
        return "make_user_say_restart"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        print('made yser say restart')
        return [UserUttered(text="/restart")]


def return_slot_values(tracker):
    d = {
        "phone_number": "Phone Number",
        "aadhar_number": "Aadhar Number",
        "id_type": "ID Type",
        "id_number": "ID Number",
        "caste": "Caste",
        "has_disability": "Disability",
        "nominee_name": "Nominee Name",
        "nominee_gender": "Nominee Gender",
        "relationship_with_nominee": "Relationship with Nominee",
        "nominee_age": "Nominee Age",
        "nominee_occupation": "Nominee Occupation",
        "nominee_annual_income": "Nominee Annual Income",
        "aadhar_address": "Aadhar Address",
        "permanent_address": "Permanent Address",
        "present_address": "Present Address",
        "user_name": "User Name",
        "user_gender": "User Gender",
        "user_religion": "Religion",
        "user_occupation": "User Occupation"
    }


class AskConfirmation(Action):
    def name(self) -> Text:
        return "action_ask_onboardingForm_confirmation"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        slot_lists = []
        dispatcher.utter_message(text="I have the following details about you.")
        dispatcher.utter_message(response="utter_slots_values")
        dispatcher.utter_message(
            text=f"To confirm please press the confirm button or you can restart or change any values.",
            buttons=[
                {"title": "Confirm", "payload": "confirm"},
                {"title": "Change", "payload": "change"},
                {"title": "Restart", "payload": "/restart"}
            ]
        )
        return []


class AskFieldToChange(Action):
    def name(self) -> Text:
        return "action_ask_onboardingForm_field_to_change"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        slot_lists = []
        buttons = [{"title": val, "payload": key} for key, val in acceptable_fields_to_change.items()]
        # buttons = ["Aadhar Number": "ID Type":"id_type","ID Number":"id_number"]
        # buttons=[
        #         {"title": "Aadhar Number", "payload": "aadhar_number"},
        #         {"title": "ID Type", "payload": "id_type"},
        #         {"title": "ID Number", "payload": "id_number"}
        #     ]
        dispatcher.utter_message(
            text=f"Select||Which Fields do you want to change",
            buttons=buttons
        )
        return []


