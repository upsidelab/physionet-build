from django.core.validators import RegexValidator


gcp_billing_account_id_validator = RegexValidator(
    "\A[A-Z0-9]{6}-[A-Z0-9]{6}-[A-Z0-9]{6}\Z",
    message='Invalid ID format. Enter an ID in the format "XXXXXX-XXXXXX-XXXXXX".',
)
