import fastapi


class Router:

    def __init__(self):
        self.router = fastapi.APIRouter(
            prefix="/status",
            tags=["status"],
        )

        self.router.add_api_route(path='/',
                                  endpoint=self.endpoint,
                                  methods=['get'])
        pass

    async def endpoint(self):
        resp = {"status": "ok"}

        return resp
