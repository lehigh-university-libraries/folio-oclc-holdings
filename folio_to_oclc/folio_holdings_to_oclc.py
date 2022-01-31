import configparser
import logging

from folio import Folio
from oclc import Oclc

logging.basicConfig()
log = logging.getLogger("FolioHoldingsToOclc")
log.setLevel(logging.DEBUG)

class FolioHoldingsToOclc:
    """ Get recent holdings from FOLIO and submit them to OCLC. """

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('test.properties')

        self.folio = Folio(self.config)

    def get_yesterday(self):
        pass

    def run_yesterdays_holdings(self):
        log.debug("Running yesterday's holdings")

        # Determine yesterday's date
        yesterday = self.get_yesterday()

        # Get from FOLIO the list of updated holdings.
        holdings = self.folio.get_updated_instance_oclc_numbers(yesterday)

        # Submit those to OCLC.
        oclc = Oclc()
        oclc.submit_holdings(holdings)

        log.debug("Finished running yesterday's holdings")

holdings_to_oclc = FolioHoldingsToOclc()
holdings_to_oclc.run_yesterdays_holdings()