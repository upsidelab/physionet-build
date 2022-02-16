from django.forms import ValidationError
from django.test import TestCase

from environment.validators import gcp_billing_account_id_validator


class BillingAccountValidatorTestCase(TestCase):
    def test_fails_for_invalid_regex(self):
        self.assertRaises(
            ValidationError, gcp_billing_account_id_validator, "some value"
        )

    def test_succeeds_for_billing_account_regex(self):
        gcp_billing_account_id_validator("XXXXXX-XXXXXX-XXXXXX")
