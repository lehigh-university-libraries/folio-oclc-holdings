import logging
from xmlrpc.client import SERVER_ERROR
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import time

from data import Record, HoldingUpdateResult

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class Oclc:
    """ Submit updated holdings via the WorldCat Metadata API v2. """

    SCOPES = ['WorldCatMetadataAPI']
    SERVICE_URL = "https://metadata.api.oclc.org/worldcat"
    TOKEN_URL = "https://oauth.oclc.org/token"
    HEADER_ACCEPT_JSON = { "Accept" : "application/json" }
    SESSION_BUFFER = 60 #seconds

    def __init__(self, config):
        self._config = config
        log.addHandler(self._config.log_file_handler)
        self._init_connection()

    def _init_connection(self):
        WS_KEY = self._config.get('Oclc', 'ws_key')
        SECRET = self._config.get('Oclc', 'secret')

        self._basic_auth = HTTPBasicAuth(WS_KEY, SECRET)
        client = BackendApplicationClient(client_id=WS_KEY, scope=Oclc.SCOPES)
        self._session = OAuth2Session(client=client)
        self._get_token()

    def _get_token(self):
        try:
            self._token = self._session.fetch_token(token_url=Oclc.TOKEN_URL, auth=self._basic_auth)
            log.debug("Got token.")
        except Exception as e:
            log.error("Error when trying to get token: " + str(e))
            raise e

    def _check_connection(self):
        """ Renew the connection if it is close to expiring. """

        if self._token['expires_at'] - time.time() <= Oclc.SESSION_BUFFER:
            log.info("Session close to expiring.  Renewing token.")
            self._get_token()

    def check_holding(self, oclc_number: str):
        """ Check holding status of a single OCLC number.  Return an object indicating
        whether or not holding is set and the currentOclcNumber. """

        self._check_connection()
        url = f"{Oclc.SERVICE_URL}/manage/institution/holdings/current?oclcNumbers={oclc_number}"
        response = self._session.get(url, headers=Oclc.HEADER_ACCEPT_JSON)
        log.debug("request url from response: " + str(response.request.url))
        log.debug("request headers from response: " + str(response.request.headers))
        log.debug("response text: " + str(response.text))
        if response.status_code == 404: # Appears no longer used in API v2, but leaving just in case
            log.debug(f"Record was not found in OCLC: {oclc_number}")
            return CheckHoldingResult(False, None)
        else:
            response.raise_for_status()
        result = response.json()
        holdings = result['holdings'][0]
        is_holding_set = holdings['holdingSet']
        current_oclc_number = holdings['currentControlNumber']
        if not current_oclc_number:
            log.debug(f"Record was not found in OCLC: {oclc_number}")
            return CheckHoldingResult(False, None)
        elif not is_holding_set:
            log.debug(f"Checked holdings for {oclc_number}: Not set.")
            return CheckHoldingResult(False, current_oclc_number);
        else:
            if current_oclc_number == oclc_number:
                log.debug(f"Checked holdings for {oclc_number}: Set.")
            else:
                log.debug(f"Checked holdings for {oclc_number}: Set with new OCLC number: {current_oclc_number}.")
            return CheckHoldingResult(True, current_oclc_number)

    def update_holding(self, record: Record) -> HoldingUpdateResult:
        if record.instance_status == Record.InstanceStatus.SET:
            return self.set_holding(record.oclc_number)
        elif record.instance_status == Record.InstanceStatus.WITHDRAWN:
            return self.delete_holding(record.oclc_number)
        else:
            log.error(f"Skipped record with unknown status: {record}")

    def set_holding(self, oclc_number: str):
        """ Set an institution holding for a single OCLC number. """

        check_holding_result = self.check_holding(oclc_number)

        # Skip the submit if the holding is already set
        if check_holding_result.is_set:
            return self._result(operation=HoldingUpdateResult.Operation.SET, success=False, 
                message=f"Failed to set holdings for record {oclc_number}. Holdings already set.")   

        # Use newer OCLC number if applicable
        oclc_number = check_holding_result.current_oclc_number

        self._check_connection()
        url = f"{Oclc.SERVICE_URL}/manage/institution/holdings/{oclc_number}/set"
        response = self._session.post(url, headers=Oclc.HEADER_ACCEPT_JSON) 
        log.debug(f"OCLC response status: {response.status_code}")
        if response.status_code == 200:
            return self._result(operation=HoldingUpdateResult.Operation.SET, success=True, 
                message=f"Holdings successfully set for record {oclc_number}")
        else:
            return self._result(operation=HoldingUpdateResult.Operation.SET, success=False, 
                message=f"Failed to set holdings for record  {oclc_number}. Unexpected status code: {response.status_code}.")                        

    def delete_holding(self, oclc_number: str):
        """ Delete (unset) an institution holding for a single OCLC number. """

        check_holding_result = self.check_holding(oclc_number)

        # Skip the submit if the holding is already unset
        if not check_holding_result.is_set:
            return self._result(operation=HoldingUpdateResult.Operation.WITHDRAW, success=False, 
                message=f"Failed to delete holdings for record {oclc_number}. Holdings not set on record.")
        
        # Use newer OCLC number if applicable
        oclc_number = check_holding_result.current_oclc_number

        self._check_connection()
        url = f"{Oclc.SERVICE_URL}/manage/institution/holdings/{oclc_number}/unset"
        response = self._session.post(url, headers=Oclc.HEADER_ACCEPT_JSON) 
        log.debug(f"OCLC response status: {response.status_code}")
        if response.status_code == 200:
            return self._result(operation=HoldingUpdateResult.Operation.WITHDRAW, success=True, 
                message=f"Holdings successfully deleted for record {oclc_number}")
        elif response.status_code == 409:
            return self._result(operation=HoldingUpdateResult.Operation.WITHDRAW, success=False, 
                message=f"Failed to delete holdings for record {oclc_number} with status code {response.status_code}. "\
                    "Your institution may have one or more local holdings records linked to this record.")                        
        else:
            return self._result(operation=HoldingUpdateResult.Operation.WITHDRAW, success=False,
                message=f"Failed to delete holdings for record {oclc_number}. Unexpected status code:  {response.status_code}.")                        

    def _result(self, operation, success, message):
        result = HoldingUpdateResult(operation, success, message)
        log.info(result.message)
        return result

class CheckHoldingResult:

    def __init__(self, is_set: bool, current_oclc_number: str):
        self.is_set = is_set
        self.current_oclc_number = current_oclc_number
