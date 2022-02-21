from django.core.validators import RegexValidator


MAX_PROJECT_DATASET_GROUP_LENGTH = 30


gcp_billing_account_id_validator = RegexValidator(
    "\A[A-Z0-9]{6}-[A-Z0-9]{6}-[A-Z0-9]{6}\Z",
    message='Invalid ID format. Enter an ID in the format "XXXXXX-XXXXXX-XXXXXX".',
)


gcp_project_dataset_group_validator = RegexValidator(
    "^[a-z](?:[-a-z0-9]{4,28}[a-z0-9])$",
    message="Invalid dataset group format.",
)
