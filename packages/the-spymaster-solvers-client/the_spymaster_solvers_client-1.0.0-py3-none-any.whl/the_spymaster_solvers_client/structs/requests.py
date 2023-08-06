from typing import List, Optional

from codenames.game import GameState
from pydantic import BaseModel

from .base import ModelIdentifier, Solver


class LoadModelsRequest(BaseModel):
    model_identifiers: List[ModelIdentifier] = []


class BaseGenerateRequest(BaseModel):
    game_state: GameState
    model_identifier: Optional[ModelIdentifier] = None
    solver: Solver = Solver.NAIVE


class GenerateHintRequest(BaseGenerateRequest):
    pass


class GenerateGuessRequest(BaseGenerateRequest):
    pass
