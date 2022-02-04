from django import forms
from environment.validators import gcp_billing_account_id_validator


class BillingAccountIdForm(forms.Form):
    billing_account_id = forms.CharField(
        label="Billing Account ID",
        max_length=20,
        validators=[gcp_billing_account_id_validator],
    )


class CreateResearchEnvironmentForm(forms.Form):
    AVAILABLE_REGIONS = [
        ("us-east1", "US East"),
    ]
    AVAILABLE_INSTANCE_TYPES = [
        ("some1", "some instance type"),
        ("some2", "test"),
    ]
    AVAILABLE_ENVIRONMENT_TYPES = [
        ("jupyter", "Jupyter"),
        ("rstudio", "RStudio"),
    ]

    region = forms.ChoiceField(label="Region", choices=AVAILABLE_REGIONS)
    instance_type = forms.ChoiceField(
        label="Instance type", choices=AVAILABLE_INSTANCE_TYPES
    )
    environment_type = forms.ChoiceField(
        label="Environment type",
        choices=AVAILABLE_ENVIRONMENT_TYPES,
        widget=forms.RadioSelect,
    )
