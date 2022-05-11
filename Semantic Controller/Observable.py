from abc import ABC, abstractmethod

import Observer


class Observable(ABC):
    """Basic Observable


    """

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        """
        Attaches an Observer

        :param observer: the observer that oversees the observable
        """
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        """
        Detaches an Observer

        :param observer: the observer that oversees the observable
        """
        pass

    @abstractmethod
    def notify(self, string: str) -> None:
        """
        This function calls the Update function of the observers.

        :param string: the message that shall be passed
        """
        pass
