# Unit tests to test the authentication module
import conftest
import pytest
from pyhpcc.errors import HPCCAuthenticationError
from pyhpcc.models.auth import Auth

HPCC_HOST = conftest.HPCC_HOST
HPCC_PORT = conftest.HPCC_PORT
HPCC_USERNAME = conftest.HPCC_USERNAME
HPCC_PASSWORD = conftest.HPCC_PASSWORD
HPCC_PROTOCOL = conftest.HPCC_PROTOCOL
DUMMY_USERNAME = conftest.DUMMY_USERNAME
DUMMY_PASSWORD = conftest.DUMMY_PASSWORD
DUMMY_HPCC_HOST = conftest.DUMMY_HPCC_HOST
DUMMY_HPCC_PORT = conftest.DUMMY_HPCC_PORT


# Test the get_username method
def test_get_username():
    test = Auth(
        HPCC_HOST,
        HPCC_PORT,
        HPCC_USERNAME,
        HPCC_PASSWORD,
        True,
        HPCC_PROTOCOL,
    )
    test.get_username() == HPCC_USERNAME


# Test the get_verified method
def test_get_verified():
    test = Auth(
        HPCC_HOST,
        HPCC_PORT,
        HPCC_USERNAME,
        HPCC_PASSWORD,
        True,
        HPCC_PROTOCOL,
    )
    assert test.get_verified()


# Test the get_verified method with an invalid username and password
def test_get_verified_invalid_username_password():
    test = Auth(
        HPCC_HOST,
        HPCC_PORT,
        DUMMY_USERNAME,
        DUMMY_PASSWORD,
        True,
        HPCC_PROTOCOL,
    )
    with pytest.raises(HPCCAuthenticationError):
        test.get_verified()


# Test the get_verified method with only required parameters
def test_get_verified_only_required_parameters():
    test = Auth(
        HPCC_HOST,
        HPCC_PORT,
        HPCC_USERNAME,
        HPCC_PASSWORD,
        protocol=HPCC_PROTOCOL,
    )
    assert test.get_verified()


# Test the get_verified method with an invalid IP address
def test_get_verified_invalid_ip():
    test = Auth(
        DUMMY_HPCC_HOST,
        HPCC_PORT,
        HPCC_USERNAME,
        HPCC_PASSWORD,
        True,
        HPCC_PROTOCOL,
    )
    with pytest.raises(HPCCAuthenticationError):
        test.get_verified()


# Test the get_verified method with an invalid port
def test_get_verified_invalid_port():
    test = Auth(
        HPCC_HOST,
        DUMMY_HPCC_PORT,
        HPCC_USERNAME,
        HPCC_PASSWORD,
        True,
        HPCC_PROTOCOL,
    )
    with pytest.raises(HPCCAuthenticationError):
        test.get_verified()
