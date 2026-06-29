from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    orchestrator_callback_url: str = "/".join(
        (
            "http://payment-orchestrator-service:8001",
            "provider-callbacks/mock-bank",
        )
    )

    approved_after_5_probability: float = Field(
        default=0.20,
        ge=0,
        le=1,
    )
    declined_after_20_probability: float = Field(
        default=0.15,
        ge=0,
        le=1,
    )
    error_after_5_probability: float = Field(
        default=0.25,
        ge=0,
        le=1,
    )
    duplicate_callback_probability: float = Field(
        default=0.05,
        ge=0,
        le=1,
    )
    callback_before_response_probability: float = Field(
        default=0.05,
        ge=0,
        le=1,
    )
    no_callback_probability: float = Field(
        default=0.30,
        ge=0,
        le=1,
    )

    approved_delay_seconds: float = Field(default=5, ge=0)
    declined_delay_seconds: float = Field(default=20, ge=0)
    error_delay_seconds: float = Field(default=5, ge=0)
    duplicate_delay_seconds: float = Field(default=1, ge=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_probability_distribution(self):
        total = sum(self.scenario_probabilities)
        if abs(total - 1.0) > 1e-9:
            message = "Mock Bank scenario probabilities must add up to 1.0"
            raise ValueError(message)
        return self

    @property
    def scenario_probabilities(self) -> tuple[float, ...]:
        return (
            self.approved_after_5_probability,
            self.declined_after_20_probability,
            self.error_after_5_probability,
            self.duplicate_callback_probability,
            self.callback_before_response_probability,
            self.no_callback_probability,
        )


settings = Settings()
