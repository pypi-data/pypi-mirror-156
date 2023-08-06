from codenames.game import Guess, Hint
from pydantic import BaseModel


class BaseResponse(BaseModel):
    status_code: int = 200


class LoadModelsResponse(BaseResponse):
    loaded_models_count: int


class GenerateHintResponse(BaseResponse):
    suggested_hint: Hint


class GenerateGuessResponse(BaseResponse):
    suggested_guess: Guess
