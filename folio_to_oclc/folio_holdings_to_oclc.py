import argparse
import configparser
import logging
from datetime import date, timedelta
from os.path import exists

from folio import Folio
from oclc import Oclc
from emailer import Emailer

from data import Record

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
        # print("Config: ", {section: dict(self.config[section]) for section in self.config.sections()})
        self._emailer = Emailer(self.config)

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

        test_records = self._load_test_records()
        if test_records:
            records = test_records
        else:
            # Get from FOLIO the list of updated holdings.
            log.debug("Using FOLIO")
            self.folio = Folio(self.config)
            records = self.folio.get_updated_records(date)

        # Submit those to OCLC.
        results = []
        oclc = Oclc(self.config)
        for record in records:
            result = oclc.update_holding(record)
            results.append(result)
        log.debug("Finished setting and/or deleting holdings data.")
        log.info(f"Results: {results}")
        self._emailer.send_results(results)

    def _load_test_records(self):
        records = []
        test_oclc_nums_to_set = self.config.get("Testing", "test_records_to_set", fallback=None)
        test_oclc_nums_to_unset = self.config.get("Testing", "test_records_to_unset", fallback=None)
        if test_oclc_nums_to_set or test_oclc_nums_to_unset:
            # TESTING PURPOSES: Ignore FOLIO and use these numbers instead.
            if test_oclc_nums_to_set:
                log.warning("Using TEST OCLC numbers to SET: " + test_oclc_nums_to_set)
                records.extend([Record(num.strip(','), Record.InstanceStatus.SET) for num in test_oclc_nums_to_set.split(" ")])
            if test_oclc_nums_to_unset:
                log.warning("Using TEST OCLC numbers to UNSET: " + test_oclc_nums_to_unset)
                records.extend([Record(num.strip(','), Record.InstanceStatus.WITHDRAWN) for num in test_oclc_nums_to_unset.split(" ")])
        return records if len(records) else None

def main():
    parser = argparse.ArgumentParser(description="Set or delete FOLIO holdings in OCLC.")
    parser.add_argument('-c, --config', dest='config_file', help='path to the properties file', default="test.properties")
    args = parser.parse_args()

    holdings_to_oclc = FolioHoldingsToOclc(args.config_file)
    # holdings_to_oclc.run_yesterdays_holdings()
    # TESTING PURPOSES: 
    holdings_to_oclc.run_holdings_for_date("2022-01-10")

if __name__ == '__main__':
    try:
        main()
    except Exception:
        log.exception("Caught exception.")
