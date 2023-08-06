import logging

from the_spymaster_util import wrap
from the_spymaster_util.http_client import BaseHttpClient

from .structs.requests import GenerateGuessRequest, GenerateHintRequest
from .structs.responses import GenerateGuessResponse, GenerateHintResponse

log = logging.getLogger(__name__)
DEFAULT_BASE_BACKEND = "http://localhost:5000"


class TheSpymasterSolversClient(BaseHttpClient):
    def __init__(self, base_backend: str = None):
        if not base_backend:
            base_backend = DEFAULT_BASE_BACKEND
        super().__init__(base_backend=base_backend)
        log.debug(f"Solvers client is using backend: {wrap(self.base_url)}")

    def generate_hint(self, request: GenerateHintRequest) -> GenerateHintResponse:
        data = self._post("generate-hint/", data=request.dict())
        return GenerateHintResponse(**data)

    def generate_guess(self, request: GenerateGuessRequest) -> GenerateGuessResponse:
        data = self._post("generate-guess/", data=request.dict())
        return GenerateGuessResponse(**data)
