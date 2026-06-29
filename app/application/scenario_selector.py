import random

from app.domain.scenarios import CallbackScenario


class ScenarioSelector:
    def __init__(self, probabilities: tuple[float, ...]):
        self.probabilities = probabilities

    def choose(self) -> CallbackScenario:
        return random.choices(
            population=list(CallbackScenario),
            weights=self.probabilities,
            k=1,
        )[0]
