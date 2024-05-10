from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class TaskStatus(str, Enum):
    ENQUEUED = 'ENQUEUED'
    CANCELLED = 'CANCELLED'
    IN_PROGRESS = 'IN_PROGRESS'
    SUCCESS = 'SUCCESS'
    CLIENT_ERROR = 'CLIENT_ERROR'
    SERVER_ERROR = 'SERVER_ERROR'


@dataclass
class TaskResult:
    status: TaskStatus
    raw_response: bytes | None = None


@dataclass
class GenericTask:
    id: UUID
    raw_request: bytes
