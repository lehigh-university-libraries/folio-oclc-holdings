import argparse
import configparser
import logging
from datetime import date, timedelta
from os.path import exists

from folio import Folio
from oclc import Oclc

from data import OclcNumber

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class FolioHoldingsToOclc:
    """ Get recent holdings from FOLIO and submit them to OCLC. """

    def __init__(self, config_file):
        if not exists(config_file):
            raise FileNotFoundError(f"Cannot find config file: {config_file}")

        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self._init_log()
        log.info(f"Initilalized with config file {config_file}")
        # Note: Config contains the wskey and secret.  Consider logging destinations.
        # log.debug("Config: ", {section: dict(self.config[section]) for section in self.config.sections()})

    def _init_log(self):
        log_file = self.config.get("Logging", "log_file", fallback=None)
        if log_file:
            self.config.log_file_handler = logging.FileHandler(filename=log_file)
            self.config.log_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            log.addHandler(self.config.log_file_handler)

    def run_yesterdays_holdings(self):
        log.debug("Running yesterday's holdings")
        yesterday = date.today() - timedelta(days=1)
        self.run_holdings_for_date(yesterday)

    def run_holdings_for_date(self, date):
        log.debug("Running holdings for date: " + str(date))

        test_oclc_nums = self.config.get("Testing", "test_oclc_nums", fallback=None)
        if test_oclc_nums:
            # TESTING PURPOSES: Ignore FOLIO and use these numbers instead.
            log.warning("Using TEST OCLC numbers: " + test_oclc_nums)
            oclc_nums = [OclcNumber(num.strip(',')) for num in test_oclc_nums.split(" ")]

        else:
            # Get from FOLIO the list of updated holdings.
            self.folio = Folio(self.config)
            oclc_nums = self.folio.get_updated_instance_oclc_numbers(date)

        # Submit those to OCLC.
        oclc = Oclc(self.config)
        for oclc_num in oclc_nums:
            # Testing purposes: Set and then delete the holding.
            oclc.set_holding(oclc_num)
            oclc.delete_holding(oclc_num)

        log.debug("Finished setting or deleting holdings data.")

def main():
    parser = argparse.ArgumentParser(description="Set or delete FOLIO holdings in OCLC.")
    parser.add_argument('-c, --config', dest='config_file', help='path to the properties file', default="test.properties")
    args = parser.parse_args()

    holdings_to_oclc = FolioHoldingsToOclc(args.config_file)
    # holdings_to_oclc.run_yesterdays_holdings()
    # TESTING PURPOSES: 
    holdings_to_oclc.run_holdings_for_date("2022-01-10")

if __name__ == '__main__':
    main()
