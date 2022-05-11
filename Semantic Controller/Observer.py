from abc import ABC, abstractmethod

import Observable


class Observer(ABC):

    @abstractmethod
    def update(self, observable: Observable, string: str) -> None:
        """
        This function gets called by the observables, by the notify function.

        :param observable: the source
        :param string: the message from the observable
        """
        pass
