"""Turkish banknote detection module
"""

__author__ = "Omar Othman"

from .base_services import KerasCnnImageService


class BanknoteService(KerasCnnImageService):
    """A service for detecting Turkish banknotes.
    """

    def __init__(self):
        service_name = "banknote"
        # banknote denominations
        class_map = {
            0: 10,
            1: 100,
            2: 20,
            3: 200,
            4: 5,
            5: 50,
        }
        super().__init__(service_name, class_map=class_map)
