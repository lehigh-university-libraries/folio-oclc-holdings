from enum import Enum

class Record:

    class InstanceStatus(Enum):
        SET = 0
        WITHDRAWN = 1

    def __init__(self, oclc_number, instance_status):
        self._raw_oclc_number = oclc_number
        self.oclc_number = self._numeric()
        self.instance_status = instance_status

    def _numeric(self):
        """ 
        Strip the leading (OcoLc).
        Also strip any leading zeroes on the number. Testing shows that numbers with leading zeroes
        are not the "current" OCLC number, and thus the holdings API calls with those numbers fail.
        """
        for index, char in enumerate(self._raw_oclc_number):
            if char.isdigit() and int(char) != 0:
                return self._raw_oclc_number[index:]
    
    def __repr__(self):
        return f"{self.oclc_number} ({self.instance_status})"

class HoldingUpdateResult:

    class Operation(Enum):
        SET = 0
        WITHDRAW = 1

    def __init__(self, operation: Operation, success: bool, message: str):
        self.operation = operation
        self.success = success
        self.message = message

    def __repr__(self):
        return self.message
