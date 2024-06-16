import logging
from dataclasses import dataclass

import requests
import sys
from loguru import logger

from arqanmode.domain.model import ModelInterface
from arqanmode.kafka.consumer import Consumer
from arqanmode.kafka.generic_consumer import GenericConsumer
from arqanmode.storage import RedisClient


class ModelRegistryClient:
    @dataclass()
    class Config:
        url: str
        port: str

    def __init__(self, config: Config):
        self.url = f"http://{config.url}:{config.port}"

    async def ping(self):
        response = requests.get(self.url + "/status")

        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "ok"

    async def register(self, model_interface: ModelInterface):
        print(model_interface.get_interface().json())
        response = requests.post(self.url + "/register",
                                 json=model_interface.get_interface().json())

        print(response)
        assert response.status_code == 200

    async def unregister(self, model_interface: ModelInterface):
        response = requests.post(self.url + "/unregister",
                                 json={
                                     "name": model_interface.get_interface().model_name,
                                 })

        assert response.status_code == 200


class ModelFramework:

    def __init__(self,
                 model: ModelInterface,
                 queue_config: GenericConsumer.Config,
                 storage_config: RedisClient.Config,
                 model_registry_config: ModelRegistryClient.Config):
        self.kafka_consumer = None
        logger.add(sys.stderr, level=logging.INFO, serialize=True, backtrace=True)

        self.model = model
        self.queue_config = queue_config

        # init and check connection to storage
        self.storage = RedisClient(storage_config)

        # init and check initial connection to registry
        self.model_registry_client = ModelRegistryClient(model_registry_config)

        # init http server for connection with world
        # heartbeats and so on
        self.http_server = None

    async def process(self):
        # register model in registry
        resp = await self.model_registry_client.register(self.model)

        # check connection to storage
        await self.storage.ping()

        # init connection to kafka
        self.kafka_consumer = Consumer(self.queue_config, self.model, self.storage)

        # process kafka messages
        await self.kafka_consumer.run()

        pass

    async def stop(self):
        # unregister model in registry
        await self.model_registry_client.unregister(self.model)
