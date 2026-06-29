from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.application.scenario_selector import ScenarioSelector
from app.domain.scenarios import CallbackScenario
from app.infrastructure.settings import Settings


def test_default_probability_distribution():
    settings = Settings(_env_file=None)

    assert settings.scenario_probabilities == (
        0.20,
        0.15,
        0.25,
        0.05,
        0.05,
        0.30,
    )


def test_probability_distribution_must_add_up_to_one():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            approved_after_5_probability=0.50,
            declined_after_20_probability=0.20,
            error_after_5_probability=0.10,
            duplicate_callback_probability=0.10,
            callback_before_response_probability=0.10,
            no_callback_probability=0.20,
        )


@patch("app.application.scenario_selector.random.choices")
def test_selector_uses_configured_weights(mock_choices):
    probabilities = (0.20, 0.15, 0.25, 0.05, 0.05, 0.30)
    mock_choices.return_value = [CallbackScenario.NO_CALLBACK]
    selector = ScenarioSelector(probabilities)

    selected = selector.choose()

    assert selected == CallbackScenario.NO_CALLBACK
    assert mock_choices.call_args.kwargs["weights"] == probabilities
