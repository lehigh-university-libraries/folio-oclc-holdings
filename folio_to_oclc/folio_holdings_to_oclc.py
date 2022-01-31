import configparser
import logging
from datetime import date, timedelta

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

    def run_yesterdays_holdings(self):
        log.debug("Running yesterday's holdings")
        yesterday = date.today() - timedelta(days=1)
        self.run_holdings_for_date(yesterday)

    def run_holdings_for_date(self, date):
        log.debug("Running holdings for date: " + str(date))

        # Get from FOLIO the list of updated holdings.
        holdings = self.folio.get_updated_instance_oclc_numbers(date)

        # Submit those to OCLC.
        oclc = Oclc()
        oclc.submit_holdings(holdings)

        log.debug("Finished running holdings for date: " + str(date))

holdings_to_oclc = FolioHoldingsToOclc()
# holdings_to_oclc.run_yesterdays_holdings()
holdings_to_oclc.run_holdings_for_date("2022-01-10")
