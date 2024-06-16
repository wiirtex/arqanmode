from loguru import logger
from pydantic import ValidationError
from redis import RedisError

from arqanmode.domain.model import ModelInterface
from arqanmode.domain.task import TaskStatus, GenericTask
from arqanmode.storage.interface import Storage
from .generic_consumer import GenericConsumer


class Consumer(GenericConsumer):
    def __init__(self, config: GenericConsumer.Config, model: ModelInterface, storage: Storage):
        super().__init__(logger, config)
        self._storage = storage
        self.model = model

    async def run(self):
        async for task in super().run():
            task_status = await self._storage.get_task_status(task.id)
            if task_status is None:
                logger.warning('no task status in storage')
                continue
            if task_status == TaskStatus.CANCELLED:
                logger.info('ignoring task because it was cancelled')
                continue

            try:
                await self._process_task(task)
            except Exception as e:
                self._logger.exception(f'failed to process task (id={str(task.id)}):', e)
                await self._storage.save_task_error(
                    task.id,
                    TaskStatus.SERVER_ERROR,
                    err_code='INTERNAL_ERROR',
                    err_msg='failed to process task'
                )

    async def _process_task(self, task: GenericTask):
        try:
            request = self.model.parse_and_validate(task.raw_request)
        except ValidationError as err:
            self._logger.warning('validation error')
            await self._storage.save_task_error(
                task.id,
                TaskStatus.CLIENT_ERROR,
                err_code='VALIDATION_ERROR',
                err_msg='request does not match request schema',
                err_details=err.errors()
            )
            return

        try:
            reqs = await self.model.process_task(request)
        except Exception as e:
            self._logger.exception('failed to process task:', e)

            await self._storage.save_task_error(
                task.id,
                TaskStatus.SERVER_ERROR,
                err_code='INTERNAL_ERROR',
                err_msg='failed to process task'
            )
            return

        try:
            await self._storage.save_task_result(task.id, reqs)
        except RedisError:
            self._logger.exception('failed to save task result')
