import logging
from folioclient.FolioClient import FolioClient

from data import OclcNumber

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class Folio:
    """ Get updated holdings via the FOLIO API. """

    def __init__(self, config):
        self._config = config
        log.addHandler(self._config.log_file_handler)
        self.connection = self._init_connection()

    def _init_connection(self):
        log.debug("Connecting to FOLIO")
        self.client = FolioClient(
            okapi_url = self._config.get('Folio', 'okapi_url'),
            tenant_id = self._config.get('Folio', 'tenant_id'),
            username = self._config.get('Folio', 'username'),
            password = self._config.get('Folio', 'password')
        )

    def get_updated_instance_oclc_numbers(self, updated_date):
        log.debug("Getting updated instance OCLC numbers")
        instances = self._get_updated_instances(updated_date)
        OCLC_ID_TYPE = self._config.get('Folio', 'id_type_oclc')
        oclc_numbers = []
        for instance in instances:
            for identifier in instance['identifiers']:
                if identifier['identifierTypeId'] == OCLC_ID_TYPE:
                    oclc_numbers.append(OclcNumber(identifier['value']))
                    # only use the first OCLC num found for each identifier
                    break
        
        if len(oclc_numbers):
            log.debug("OCLC numbers: " + str(oclc_numbers))
        else:
            log.debug("No OCLC numbers found")

    def _get_updated_instances(self, updated_date):
        path = "/inventory/instances"
        status_id_oclc = self._config.get('Folio', 'instance_status_oclc')
        params = f'?query=(statusUpdatedDate=={updated_date}* and statusId="{status_id_oclc}")'
        result = self.client.folio_get(path, query = params)
        instances = result['instances']
        return instances
