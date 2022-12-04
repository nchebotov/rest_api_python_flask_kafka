import pytest
from flask import current_app
from app.app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            assert current_app.config["ENV"] == "production"
        yield client


# @pytest.fixture(scope='module')
# def url():
#     url = 'http://localhost:5000/'
#     return url
