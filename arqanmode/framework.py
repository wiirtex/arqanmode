import logging

import requests
import sys
from loguru import logger

from arqanmode.domain.model import ModelInterface
from arqanmode.kafka.consumer import Consumer
from arqanmode.kafka.generic_consumer import GenericConsumer
from arqanmode.storage.storage import Storage


class ModelFramework:

    def __init__(self,
                 model: ModelInterface,
                 queue_config: GenericConsumer.Config,
                 storage: Storage):
        self.kafka_consumer = None
        logger.add(sys.stderr, level=logging.INFO, serialize=True, backtrace=True)

        self.model = model
        self.queue_config = queue_config

        # init and check connection to storage
        self.storage = storage

        # init and check initial connection to registry
        self.model_registry_client = ModelRegistryClient("http://localhost:8000")

        # init http server for connection with world
        # heartbeats and so on
        self.http_server = None

    def _validate_model(self):
        get_interface = getattr(self.model, "validate")
        if not callable(get_interface):
            raise Exception("model.validate is not callable")

        # get_interface = getattr(self.model, "")

    def _validate_models_interface(self, interface):
        pass

    async def process(self):
        # register model in registry
        resp = await self.model_registry_client.register(self.model)
        print("arqanmode: ", resp)

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


class ModelRegistryClient:

    def __init__(self, url: str):
        self.url = url

    async def ping(self):
        response = requests.get(self.url + "/status")

        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "ok"

    async def register(self, model_interface: ModelInterface):
        print(model_interface.get_interface().json())
        response = requests.post(self.url + "/register",
                                 data=model_interface.get_interface().json())

        print(response)
        assert response.status_code == 200

    async def unregister(self, model_interface: ModelInterface):
        response = requests.post(self.url + "/unregister",
                                 json={
                                     "name": model_interface.get_interface().model_name,
                                 })

        assert response.status_code == 200
