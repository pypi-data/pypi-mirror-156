from typing import List, Optional

from codenames.game import GameState
from pydantic import BaseModel

from .base import ModelIdentifier, Solver


class LoadModelsRequest(BaseModel):
    model_identifiers: List[ModelIdentifier] = []


class BaseGenerateRequest(BaseModel):
    solver: Solver = Solver.NAIVE
    model_identifier: Optional[ModelIdentifier] = None
    game_state: GameState


class GenerateHintRequest(BaseGenerateRequest):
    pass


class GenerateGuessRequest(BaseGenerateRequest):
    pass
