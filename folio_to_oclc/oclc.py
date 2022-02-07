import logging
from xmlrpc.client import SERVER_ERROR
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

from data import FolioOclcHoldingsError, Record

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class Oclc:
    """ Submit updated holdings via the OCLC API. """

    SCOPES = ['WorldCatMetadataAPI']
    SERVICE_URL = "https://worldcat.org"
    TOKEN_URL = "https://oauth.oclc.org/token"
    HEADER_ACCEPT_JSON = { "Accept" : "application/json" }

    def __init__(self, config):
        self._config = config
        log.addHandler(self._config.log_file_handler)
        self._init_oclc_metadata()
        self._session = self._init_connection()

    def _init_oclc_metadata(self):
        # Not yet needed; may remove.
        # self._inst_symbol = self._config.get('Oclc', 'inst_symbol', fallback=None)
        # self._inst_registry_id = self._config.get('Oclc', 'inst_registry_id', fallback=None)
        # if not self._inst_symbol and not self._inst_registry_id:
        #     raise FolioOclcHoldingsError("Properties must define either inst_registry_id or inst_symbol.")
        pass

    def _init_connection(self):
        WS_KEY = self._config.get('Oclc', 'ws_key')
        SECRET = self._config.get('Oclc', 'secret')

        basic_auth = HTTPBasicAuth(WS_KEY, SECRET)
        client = BackendApplicationClient(client_id=WS_KEY, scope=Oclc.SCOPES)
        session = OAuth2Session(client=client)
        try:
            self._token = session.fetch_token(token_url=Oclc.TOKEN_URL, auth=basic_auth)
            log.debug("Got token.")
        except Exception as e:
            log.error("Error when trying to get token: " + str(e))
            raise e

        return session

    def check_holding(self, oclc_number: str):
        """ Check holding status of a single OCLC number. """
        url = f"{Oclc.SERVICE_URL}/ih/checkholdings?oclcNumber={oclc_number}";
        response = self._session.get(url, headers=Oclc.HEADER_ACCEPT_JSON)
        if response.status_code == 404:
            log.info(f"Record was not found in OCLC: {oclc_number}")
            return False
        else:
            response.raise_for_status()
        result = response.json()
        is_holding_set = result['isHoldingSet']
        log.debug(f"Checked holdings for {oclc_number}: {is_holding_set}; response: {result}")
        return is_holding_set

    def update_holding(self, record: Record):
        match record.instance_status:
            case Record.InstanceStatus.SET:
                self.set_holding(record.oclc_number)
            case Record.InstanceStatus.WITHDRAWN:
                self.delete_holding(record.oclc_number)
            case _:
                log.error(f"Skipped record with unknown status: {record}")


    def set_holding(self, oclc_number: str):
        """ Set an institution holding for a single OCLC number. """

        # Skip the submit if the holding is already registered
        if self.check_holding(oclc_number):
            log.info(f"OCLC num already registered: {oclc_number}")
            return

        url = f"{Oclc.SERVICE_URL}/ih/data?oclcNumber={oclc_number}"
        response = self._session.post(url, headers=Oclc.HEADER_ACCEPT_JSON) 
        response.raise_for_status()
        log.info(f"Set holding for item {oclc_number}")
        log.debug(f"OCLC response status: {response.status_code}")

    def delete_holding(self, oclc_number: str):
        """ Delete an institution holding for a single OCLC number. """

        url = f"{Oclc.SERVICE_URL}/ih/data?oclcNumber={oclc_number}&cascade=0"
        response = self._session.delete(url, headers=Oclc.HEADER_ACCEPT_JSON) 
        response.raise_for_status()
        log.info(f"Deleted holding for item {oclc_number}")
        log.debug(f"OCLC response status: {response.status_code}")
