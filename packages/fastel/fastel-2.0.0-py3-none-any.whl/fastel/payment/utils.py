from enum import Enum


class PaymentStatus(str, Enum):
    WAITING = "waiting"
    SUCCESS = "success"
    FAILURE = "failure"
    CODE_GENERATED = "code_generated"
