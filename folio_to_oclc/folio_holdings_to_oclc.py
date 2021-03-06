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
log.setLevel(logging.INFO)

class FolioHoldingsToOclc:
    """ Get recent holdings from FOLIO and submit them to OCLC. """

    def __init__(self, config_file):
        if not exists(config_file):
            raise FileNotFoundError(f"Cannot find config file: {config_file}")

        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self._init_log()
        log.info(f"Initialized with config file {config_file}")
        # Note: Config contains the wskey and secret.  Consider logging destinations.
        # print("Config: ", {section: dict(self.config[section]) for section in self.config.sections()})
        self._emailer = Emailer(self.config)

    def _init_log(self):
        log_file = self.config.get("Logging", "log_file", fallback=None)
        if log_file:
            self.config.log_file_handler = logging.FileHandler(filename=log_file)
            self.config.log_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            log.addHandler(self.config.log_file_handler)
        else:
            self.config.log_file_handler = logging.NullHandler()

    def run(self, query_date=None):
        """ Run a holdings update process.  
        
        Use yesterday's updated records, or a given date's record if specified, 
        or test records if specified in the config file.
        """
        test_records = self._load_test_records()
        if test_records:
            records = test_records
            job_description = "Setting & withdrawing holdings on specified test records"
        elif query_date:
            (records, job_description) = self.load_records_updated_on_date(query_date)
        else:
            (records, job_description) = self.load_records_updated_yesterday()

        results = self.send_updates_to_oclc(records)
        self.email_results(results, job_description)

    def load_records_updated_yesterday(self):
        log.debug("Loading yesterday's updated records")
        yesterday = date.today() - timedelta(days=1)
        return self.load_records_updated_on_date(yesterday)

    def load_records_updated_on_date(self, date):
        job_description = f"Setting & withdrawing holdings updated on date: {date}."
        log.info(job_description)

        self.folio = Folio(self.config)
        (records, records_summary) = self.folio.get_updated_records(date)
        job_description += f"  {records_summary}"
        return (records, job_description)

    def send_updates_to_oclc(self, records):
        # Submit those to OCLC.
        results = []
        oclc = Oclc(self.config)
        for record in records:
            result = oclc.update_holding(record)
            results.append(result)
        log.debug("Finished setting and/or deleting holdings data.")
        return results

    def email_results(self, results, job_description):
        log.debug(f"Results: {results}")
        self._emailer.send_results(results, job_description)

    def _load_test_records(self):
        records = []
        test_oclc_nums_to_set = self.config.get("Testing", "test_records_to_set", fallback=None)
        test_oclc_nums_to_withdraw = self.config.get("Testing", "test_records_to_withdraw", fallback=None)
        if test_oclc_nums_to_set or test_oclc_nums_to_withdraw:
            # TESTING PURPOSES: Ignore FOLIO and use these numbers instead.
            if test_oclc_nums_to_set:
                log.warning("Using TEST OCLC numbers to SET: " + test_oclc_nums_to_set)
                records.extend([Record(num.strip(','), Record.InstanceStatus.SET) for num in test_oclc_nums_to_set.split(" ")])
            if test_oclc_nums_to_withdraw:
                log.warning("Using TEST OCLC numbers to WITHDRAW: " + test_oclc_nums_to_withdraw)
                records.extend([Record(num.strip(','), Record.InstanceStatus.WITHDRAWN) for num in test_oclc_nums_to_withdraw.split(" ")])
        return records if len(records) else None

def main():
    parser = argparse.ArgumentParser(description="Set or delete FOLIO holdings in OCLC.")
    parser.add_argument('-c,', '--config', dest='config_file', required=True, help='Path to the properties file')
    parser.add_argument('-d', '--date', dest='query_date', type=date.fromisoformat, help='Date of FOLIO updates to query, format YYYY-MM-DD.  Default is yesterday.')
    args = parser.parse_args()

    holdings_to_oclc = FolioHoldingsToOclc(args.config_file)
    holdings_to_oclc.run(args.query_date)

if __name__ == '__main__':
    try:
        main()
    except Exception:
        log.exception("Caught exception.")
