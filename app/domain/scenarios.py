from enum import Enum


class CallbackScenario(str, Enum):
    APPROVED_AFTER_5 = "approved_after_5"
    DECLINED_AFTER_20 = "declined_after_20"
    DUPLICATE_CALLBACK = "duplicate_callback"
    CALLBACK_BEFORE_RESPONSE = "callback_before_response"
    NO_CALLBACK = "no_callback"
