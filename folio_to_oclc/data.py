class OclcNumber:

    def __init__(self, raw):
        self.raw = raw
        self.numeric = self._numeric()

    def _numeric(self):
        for index, char in enumerate(self.raw):
            if char.isdigit():
                return self.raw[index:]
    
    def __repr__(self):
        return self.numeric

class FolioOclcHoldingsError(Exception):
    pass