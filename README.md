# Folio Holdings to OCLC

Set and withdraw holdings in OCLC based on recently updated FOLIO records.  The tool utilizes the FOLIO and OCLC APIs and is intended to run daily via a scheduled task / cron.  It has no UI but emails out a report when complete.


## Dependencies

The tool requires Python 3.x+.

### Install from PIP
  - requests
  - requests_oauthlib

### Additional Dependencies
- [FOLIO-FSE/FolioClient (python wrapper for FOLIO API)](https://github.com/FOLIO-FSE/FolioClient)

## Configuration

Copy/rename `example.properties` and configure its parameters.  Not all parameters are defined below.

### Folio Section

For connecting to and using the FOLIO APIs.  All properties are **required**.  Notes:

- `instance_status_set` and `instance_status_withdrawn`: the UUIDs corresponding to the FOLIO "instance status" that indicates a record's holdings should be set or withdrawn (respectively) in OCLC.  These IDs can be determined from a call to the FOLIO [Get /instance-statuses](https://s3.amazonaws.com/foliodocs/api/mod-inventory-storage/p/instance-status.html#instance_statuses_get) API.

- `id_type_oclc` is UUID for the FOLIO "identifier type" corresponding to an OCLC number.   Can be determined from a call to the FOLIO [Get /identifier-types](https://s3.amazonaws.com/foliodocs/api/mod-inventory-storage/p/identifier-type.html#identifier_types_get) API.

- `instances_limit` defines the maximum number of updated instances that the FOLIO API should return.  Set this to a number greater than your maximum number of potential updates per day.  See [API documentation for limit parameter](https://s3.amazonaws.com/foliodocs/api/mod-inventory/p/inventory.html#inventory_instances_get) for the theoretical maximum of 2 billion.

### Oclc Section

Properties to connect to the OCLC API.  Both properties are **required**.

### Email Section

For sending a report email after operation.  All properties are **required**.

### Logging Section

Program output is written to the specified `log_file`.  All properties are **optional**.

### Testing Section

For testing OCLC operations against specific records (see details).  All properties are **optional**.

- `test_records_to_set` and `test_records_to_withdraw` are each comma-separarted lists of OCLC numbers.  If either or both properties are set, the tool will set or withdraw (respectively) holdings for the specified OCLC numbers.  No connection to FOLIO will be made.

## How to Run

### From Command Line

py .\folio_to_oclc\folio_holdings_to_oclc.py --config=CONFIG_FILE



### From Another Module

import foliio_holdings_to_oclc  
app = folio_holdings_to_oclc.FolioHoldingsToOclc(CONFIG_FILE)  
app.run() 