from abc import ABC, abstractmethod


class Pack(ABC):
    @abstractmethod
    def get_default_service_name(self):
        pass

    @abstractmethod
    def get_description(self):
        pass

    @abstractmethod
    def get_files(self):
        pass
