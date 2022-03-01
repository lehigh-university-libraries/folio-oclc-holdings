import logging
from folioclient.FolioClient import FolioClient

from data import Record

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class Folio:
    """ Get updated holdings via the FOLIO API. """

    def __init__(self, config):
        self._config = config
        self._status_id_set = self._config.get('Folio', 'instance_status_set')
        self._status_id_withdrawn = self._config.get('Folio', 'instance_status_withdrawn')
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

    def get_updated_records(self, updated_date):
        log.debug("Getting updated instance OCLC numbers")
        instances = self._api_get_updated_instances(updated_date)
        OCLC_ID_TYPE = self._config.get('Folio', 'id_type_oclc')
        records = []
        counter = 0
        for instance in instances:
            counter += 1
            if not 'statusId' in instance:
                continue
            for identifier in instance['identifiers']:
                if identifier['identifierTypeId'] == OCLC_ID_TYPE:
                    if instance['statusId'] == self._status_id_set:
                        record = Record(oclc_number=identifier['value'], instance_status=Record.InstanceStatus.SET)
                    elif instance['statusId'] == self._status_id_withdrawn:
                        record = Record(oclc_number=identifier['value'], instance_status=Record.InstanceStatus.WITHDRAWN)
                    else:
                        log.debug(f"Skipping updated record {identifier['value']} with unhandled instance status type {instance['statusId']}.")
                        break
                    log.debug(f"Found updated FOLIO record with identifierType OCLC: {record}")
                    records.append(record)
                    # only use the first OCLC num found for each identifier
                    break
        
        records_summary = f"Found {counter:,} FOLIO instances whose status updated date changed, with {len(records):,} to either set or withdraw in OCLC."
        log.info(records_summary)
        return (records, records_summary)

    def _api_get_updated_instances(self, updated_date):
        instances_limit = self._config.get("Folio", "instances_limit")
        path = "/inventory/instances"
        params = f'?limit={instances_limit}&query=(statusUpdatedDate=={updated_date}*)'
        result = self.client.folio_get(path, query = params)
        instances = result['instances']
        return instances
