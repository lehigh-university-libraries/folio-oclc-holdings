import logging

logging.basicConfig()
log = logging.getLogger("FolioHoldingsToOclc")
log.setLevel(logging.DEBUG)

class FolioHoldingsToOclc:
    """ Get recent holdings from FOLIO and submit them to OCLC. """

    class Folio:
        """ Get updated holdings via the FOLIO API. """

        def __init__(self):
            pass

        def get_updated_holdings(self, updated_date):
            pass

    class Oclc:
        """ Submit updated holdings via the OCLC API. """

        def __init__(self):
            pass

        def submit_holdings(self, holdingsIds):
            pass

    def get_yesterday(self):
        pass

    def run_yesterdays_holdings(self):
        log.debug("Running yesterday's holdings")

        # Determine yesterday's date
        yesterday = self.get_yesterday()

        # Get from FOLIO the list of updated holdings.
        folio = self.Folio()
        holdings = folio.get_updated_holdings(yesterday)

        # Submit those to OCLC.
        oclc = self.Oclc()
        oclc.submit_holdings(holdings)

        log.debug("Finished running yesterday's holdings")

FolioHoldingsToOclc().run_yesterdays_holdings()