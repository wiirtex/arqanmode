from abc import ABC, abstractmethod

from .scheme import ModelV1
from .task import TaskResult


class ModelInterface(ABC):

    @abstractmethod
    def get_interface(self) -> ModelV1:
        """

        :return: interface of the Model, in format of
        """
        raise NotImplementedError()

    @abstractmethod
    def parse_and_validate(self, raw_request: bytes) -> object:
        """
        must parse the request and should validate it to be sure,
        that input is processable

        :param raw_request: bytes - valid json of possibly
            invalid model's input in binary format
        :return: parsed input, that will be passed as an argument to
        model's  process_task() function
        """
        raise NotImplementedError()

    @abstractmethod
    async def process_task(self, input: object) -> TaskResult:
        """
        must process parsed input, should not raise validation error

        :param input: parsed input,
            returned by model's parse_and_validate() method
        :return: domain.TaskResult
        """
        raise NotImplementedError()
