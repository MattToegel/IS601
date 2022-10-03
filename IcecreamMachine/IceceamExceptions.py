class OutOfStockException(Exception):
    """Raised when something is out of stock"""
    pass

class NeedsCleaningException(Exception):
    """Raised when the icecream machine needs cleaning"""
    pass

class InvalidChoiceException(Exception):
    """Raised when an invalid choice is picked"""
    pass

class ExceededRemainingChoicesException(Exception):
    """Raised when there are too many scoops of icecream"""
    pass

class InvalidPaymentException(Exception):
    """Raised when an invalid payment amount is given"""
    pass