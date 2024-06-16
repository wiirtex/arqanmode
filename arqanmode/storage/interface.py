from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from arqanmode.domain.task import TaskStatus, TaskResult


class Storage(ABC):
    NAME = 'storage'

    @abstractmethod
    async def get_task_status(self, task_id: UUID) -> TaskStatus | None:
        raise NotImplementedError()

    @abstractmethod
    async def get_task_result(self, task_id: UUID) -> TaskResult | None:
        raise NotImplementedError()

    @abstractmethod
    async def save_task_status(self, task_id: UUID, status: TaskStatus):
        raise NotImplementedError()

    @abstractmethod
    async def save_task_result(self, task_id: UUID, reqs: list[str]):
        raise NotImplementedError()

    @abstractmethod
    async def ping(self):
        raise NotImplementedError()

    @abstractmethod
    async def save_task_error(
            self,
            task_id: UUID,
            task_status: TaskStatus,
            *,
            err_code: str,
            err_msg: str,
            err_details: Any | None = None
    ):
        raise NotImplementedError()

    @abstractmethod
    async def close(self):
        raise NotImplementedError()
