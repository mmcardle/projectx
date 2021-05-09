import pytest

from fastapi import APIRouter, FastAPI


@pytest.fixture()
def app():
    return FastAPI()


@pytest.fixture()
def router():
    return APIRouter()
