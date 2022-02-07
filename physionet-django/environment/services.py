import requests

from user.models import User
from environment.entities import BillingAccountRequestData, BillingAccountResponseData


class ResearchEnvironmentService:
    _base_url = "https://uoftworkspacecontroller-apigateway-73a0ulw7.ts.gateway.dev/{}"

    @classmethod
    def set_up_billing_account(cls, user: User) -> BillingAccountResponseData:
        data = BillingAccountRequestData(
            familyname=user.profile.last_name,
            givenname=user.profile.first_names.split(" ")[0],
            userid=user.username,
        )
        
        try:
            response = requests.post(cls._get_url(uri="user"), data=data.dict())
        except requests.RequestException:
            # handle error here
            pass

        return BillingAccountResponseData(**response.json())


    @classmethod
    def _get_url(cls, uri: str) -> str:
        return cls._base_url.format(uri)
