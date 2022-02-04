# Folio Holdings to OCLC

Determine instances updated yesterday within FOLIO, and set or delete holdings appropriately within OCLC.

## Dependencies
### From PIP
  - requests
  - requests_oauthlib

### Others
- [FolioClient (python wrapper for API)](https://github.com/FOLIO-FSE/FolioClient)

# How to run

## From command line

py .\folio_to_oclc\folio_holdings_to_oclc.py [-config=CONFIG_FILE]

## From another module

import foliio_holdings_to_oclc
app = folio_holdings_to_oclc.FolioHoldingsToOclc(CONFIG_FILE)
app.run_yesterdays_holdings() 