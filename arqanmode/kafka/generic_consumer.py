import asyncio
from dataclasses import dataclass
from typing import AsyncIterator
from uuid import uuid4, UUID

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from aiokafka.helpers import create_ssl_context
from loguru import logger

from arqanmode.domain.task import GenericTask


class GenericConsumer:
    @dataclass(slots=True)
    class Config:
        topic: str
        group_id: str
        server: str
        secure: bool
        username: str
        password: str
        ca_file: str

    def __init__(self, logger: logger, config: Config):
        self._logger = logger
        params = {
            'bootstrap_servers': config.server,
            'group_id': config.group_id,
            'client_id': uuid4().hex,
            'auto_commit_interval_ms': 1000
        }
        if config.secure:
            params.update(
                {
                    'security_protocol': 'SASL_SSL',
                    'sasl_mechanism': 'SCRAM-SHA-512',
                    'sasl_plain_username': config.username,
                    'sasl_plain_password': config.password,
                    'ssl_context': create_ssl_context(cafile=config.ca_file)
                }
            )
        self._consumer = AIOKafkaConsumer(config.topic, **params)

    async def run(self) -> AsyncIterator[GenericTask]:
        await self._consumer.start()
        self._logger.info('connected to kafka cluster')
        try:
            async for msg in self._consumer:
                task = self._parse_message(msg)
                if task is not None:
                    self._logger.info(f'extracted task from topic: {str(task.id)}')
                    yield task
        except asyncio.CancelledError:
            self._logger.info('got cancellation signal')
        except Exception as e:
            self._logger.exception('unexpected error', e)
        finally:
            await self._consumer.stop()
            self._logger.info('stopped consuming messages')

    def _parse_message(self, msg: ConsumerRecord[bytes, bytes]) -> GenericTask | None:
        if msg.key is None:
            self._logger.warning('message has no key')
            return None
        try:
            key = msg.key.decode('utf-8')
        except UnicodeDecodeError:
            self._logger.warning(f'failed to decode message key: {msg.key}')
            return None
        try:
            task_id = UUID(key)
        except ValueError:
            self._logger.warning(f'message has invalid key: {msg.key}')
            return None
        return GenericTask(id=task_id, raw_request=msg.value)

    async def close(self):
        await self._consumer.stop()
