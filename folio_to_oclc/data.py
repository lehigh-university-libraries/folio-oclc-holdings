from enum import Enum

class Record:

    class InstanceStatus(Enum):
        OCLC = 0
        NO_OCLC = 1

    def __init__(self, oclc_number, instance_status):
        self._raw_oclc_number = oclc_number
        self.oclc_number = self._numeric()
        self.instance_status = instance_status

    def _numeric(self):
        for index, char in enumerate(self._raw_oclc_number):
            if char.isdigit():
                return self._raw_oclc_number[index:]
    
    def __repr__(self):
        return f"{self.oclc_number} ({self.instance_status})"

class FolioOclcHoldingsError(Exception):
    pass