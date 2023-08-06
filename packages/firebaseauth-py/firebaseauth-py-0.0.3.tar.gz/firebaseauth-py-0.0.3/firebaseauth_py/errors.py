# Firebase Auth Errors: https://firebase.google.com/docs/auth/admin/errors

from dataclasses import dataclass
from typing import List


@dataclass
class ErrorItem:
    domain: str
    reason: str
    mesage: str


@dataclass
class ErrorPayload:
    errors: List[ErrorItem]
    code: int
    message: str


@dataclass
class ErrorResponse:
    error: ErrorPayload
