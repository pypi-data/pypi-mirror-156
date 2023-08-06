from dataclasses import dataclass
from typing import TypedDict, Union

import requests

from .errors import ErrorResponse


class SignUpRequest(TypedDict):
    email: str
    password: str
    returnSecureToken: bool


@dataclass
class SignUpResponse:
    idToken: str
    email: str
    refreshToken: str
    expiresIn: str
    localId: str
    kind: str


class SignInWithPasswordRequest(TypedDict):
    email: str
    password: str
    returnSecureToken: bool


@dataclass
class SignInWithPasswordResponse:
    idToken: str
    email: str
    localId: str
    registered: bool
    displayName: str
    kind: str


class FetchProvidersForEmailRequest(TypedDict):
    identifier: str
    continueUri: str


@dataclass
class FetchProvidersForEmailResponse:
    kind: str
    registered: bool
    sessionId: str


@dataclass
class FirebaseAuthClient:
    api_key: str

    def url(self, endpoint: str) -> str:
        return "https://identitytoolkit.googleapis.com/v1/{}?key={}".format(
            endpoint,
            self.api_key,
        )

    def sign_up(
        self,
        email: str,
        password: str,
        return_secure_token: bool = False,
    ) -> Union[SignUpResponse, ErrorResponse]:
        payload = SignUpRequest(
            email=email,
            password=password,
            returnSecureToken=return_secure_token,
        )
        with requests.Session() as client:
            r = client.post(self.url("accounts:signUp"), data=payload)
            if "error" in r.json().keys():
                return ErrorResponse(**r.json())
            return SignUpResponse(**r.json())

    def sign_in_with_password(
        self,
        email: str,
        password: str,
        return_secure_token: bool = False,
    ) -> Union[SignInWithPasswordResponse, ErrorResponse]:
        payload = SignInWithPasswordRequest(
            email=email,
            password=password,
            returnSecureToken=return_secure_token,
        )
        with requests.Session() as client:
            r = client.post(self.url("accounts:signInWithPassword"), data=payload)
            if "error" in r.json().keys():
                return ErrorResponse(**r.json())
            return SignInWithPasswordResponse(**r.json())

    def fetch_providers_for_email(
        self,
        identifier: str,
        continue_uri: str,
    ) -> Union[FetchProvidersForEmailResponse, ErrorResponse]:
        payload = FetchProvidersForEmailRequest(
            identifier=identifier,
            continueUri=continue_uri,
        )
        with requests.Session() as client:
            r = client.post(self.url("accounts:createAuthUri"), data=payload)
            if "error" in r.json().keys():
                return ErrorResponse(**r.json())
            return FetchProvidersForEmailResponse(**r.json())
