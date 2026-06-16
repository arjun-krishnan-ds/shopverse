class InsufficientStock(Exception):
    """
    Raised when a product variant does not have enough stock
    to fulfil a requested quantity during checkout.
    """
    pass