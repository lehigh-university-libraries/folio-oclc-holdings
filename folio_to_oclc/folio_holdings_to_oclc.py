import configparser
import logging
from datetime import date, timedelta

from folio import Folio
from oclc import Oclc

from data import OclcNumber

logging.basicConfig()
log = logging.getLogger("FolioHoldingsToOclc")
log.setLevel(logging.DEBUG)

class FolioHoldingsToOclc:
    """ Get recent holdings from FOLIO and submit them to OCLC. """

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('test.properties')

        # Note: Config contains the wskey and secret.  Consider logging destinations.
        # log.debug("Inititlized with config: ", {section: dict(self.config[section]) for section in self.config.sections()})

        self.folio = Folio(self.config)

    def run_yesterdays_holdings(self):
        log.debug("Running yesterday's holdings")
        yesterday = date.today() - timedelta(days=1)
        self.run_holdings_for_date(yesterday)

    def run_holdings_for_date(self, date):
        log.debug("Running holdings for date: " + str(date))

        test_oclc_nums = self.config.get("Testing", "test_oclc_nums", fallback=None)
        if test_oclc_nums:
            # TESTING PURPOSES: Ignore FOLIO and use these numbers instead.
            log.warn("Using TEST OCLC numbers: " + test_oclc_nums)
            oclc_nums = [OclcNumber(num.strip(',')) for num in test_oclc_nums.split(" ")]

        else:
            # Get from FOLIO the list of updated holdings.
            oclc_nums = self.folio.get_updated_instance_oclc_numbers(date)

        # Submit those to OCLC.
        oclc = Oclc(self.config)
        for oclc_num in oclc_nums:
            # Testing purposes: Set and then delete the holding.
            oclc.set_holding(oclc_num)
            oclc.delete_holding(oclc_num)

        log.debug("Finished setting or deleting holdings data.")

holdings_to_oclc = FolioHoldingsToOclc()
# holdings_to_oclc.run_yesterdays_holdings()
# TESTING PURPOSES: 
holdings_to_oclc.run_holdings_for_date("2022-01-10")
