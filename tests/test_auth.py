# Unit tests to test the authentication module
import unittest

import config

from pyhpcc.auth import Auth
from pyhpcc.errors import HPCCAuthenticationError


class TestAuth(unittest.TestCase):
    HPCC_HOST = config.HPCC_HOST
    HPCC_PORT = config.HPCC_PORT
    HPCC_USERNAME = config.HPCC_USERNAME
    HPCC_PASSWORD = config.HPCC_PASSWORD
    DUMMY_USERNAME = config.DUMMY_USERNAME
    DUMMY_PASSWORD = config.DUMMY_PASSWORD
    DUMMY_HPCC_HOST = config.DUMMY_HPCC_HOST
    DUMMY_HPCC_PORT = config.DUMMY_HPCC_PORT

    # Test the get_url method
    def test_get_url(self):
        test = Auth(
            self.HPCC_HOST,
            self.HPCC_PORT,
            self.HPCC_USERNAME,
            self.HPCC_PASSWORD,
            True,
            "https",
        )
        self.assertEqual(
            test.get_url(), "https://" + self.HPCC_HOST + ":" + str(self.HPCC_PORT)
        )

    # Test the get_username method
    def test_get_username(self):
        test = Auth(
            self.HPCC_HOST,
            self.HPCC_PORT,
            self.HPCC_USERNAME,
            self.HPCC_PASSWORD,
            True,
            "https",
        )
        self.assertEqual(test.get_username(), self.HPCC_USERNAME)

    # Test the get_verified method
    def test_get_verified(self):
        test = Auth(
            self.HPCC_HOST,
            self.HPCC_PORT,
            self.HPCC_USERNAME,
            self.HPCC_PASSWORD,
            True,
            "https",
        )
        self.assertTrue(test.get_verified())

    # Test the get_verified method with an invalid username and password
    def test_get_verified_invalid_username_password(self):
        test = Auth(
            self.HPCC_HOST,
            self.HPCC_PORT,
            self.DUMMY_USERNAME,
            self.DUMMY_PASSWORD,
            True,
            "https",
        )
        self.assertRaises(HPCCAuthenticationError, test.get_verified)

    # Test the get_verified method with an invalid IP address
    def test_get_verified_invalid_ip(self):
        test = Auth(
            self.DUMMY_HPCC_HOST,
            self.HPCC_PORT,
            self.HPCC_USERNAME,
            self.HPCC_PASSWORD,
            True,
            "https",
        )
        self.assertRaises(HPCCAuthenticationError, test.get_verified)

    # Test the get_verified method with an invalid port
    def test_get_verified_invalid_port(self):
        test = Auth(
            self.HPCC_HOST,
            self.DUMMY_HPCC_PORT,
            self.HPCC_USERNAME,
            self.HPCC_PASSWORD,
            True,
            "https",
        )
        self.assertRaises(HPCCAuthenticationError, test.get_verified)

    # Test the get_verified method with only required parameters
    def test_get_verified_only_required_parameters(self):
        test = Auth(
            self.HPCC_HOST, self.HPCC_PORT, self.HPCC_USERNAME, self.HPCC_PASSWORD
        )
        self.assertTrue(test.get_verified())


if __name__ == "__main__":
    unittest.main()
