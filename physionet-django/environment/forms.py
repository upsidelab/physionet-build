from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from environment.validators import gcp_billing_account_id_validator
from environment.models import ProjectDatasetGroup


class BillingAccountIdForm(forms.Form):
    billing_account_id = forms.CharField(
        label="Billing Account ID",
        max_length=20,
        validators=[gcp_billing_account_id_validator],
    )


class CreateResearchEnvironmentForm(forms.Form):
    AVAILABLE_REGIONS = [
        ("us-central1", "us-central1"),
        ("northamerica-northeast1", "northamerica-northeast1"),
        ("europe-west3", "europe-west3"),
        ("australia-southeast1", "australia-southeast1"),
    ]
    AVAILABLE_INSTANCE_TYPES = [
        ("n1-standard-1", "n1-standard-1"),
        ("n1-standard-2", "n1-standard-2"),
        ("n1-standard-4", "n1-standard-4"),
        ("n1-standard-8", "n1-standard-8"),
        ("n1-standard-16", "n1-standard-16"),
    ]
    AVAILABLE_ENVIRONMENT_TYPES = [
        ("jupyter", "Jupyter"),
        ("rstudio", "RStudio"),
    ]

    region = forms.ChoiceField(label="Region", choices=AVAILABLE_REGIONS)
    instance_type = forms.ChoiceField(
        label="Instance type",
        choices=AVAILABLE_INSTANCE_TYPES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    environment_type = forms.ChoiceField(
        label="Environment type",
        choices=AVAILABLE_ENVIRONMENT_TYPES,
        widget=forms.RadioSelect,
    )
    persistent_disk = forms.IntegerField(
        label="Persistent data disk size",
        validators=[MinValueValidator(0), MaxValueValidator(64000)],
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        environment_type = cleaned_data.get("environment_type")
        persistent_disk = cleaned_data.get("persistent_disk")

        if environment_type == self.AVAILABLE_ENVIRONMENT_TYPES[0][0]:  # Jupyter
            if persistent_disk is None:
                raise ValidationError(
                    "Disk parameter is required for Jupyter environments."
                )


class GcpProjectDatasetGroupForm(forms.ModelForm):
    class Meta:
        model = ProjectDatasetGroup
        fields = ("name",)
        labels = {"name": "Dataset Group Name"}
