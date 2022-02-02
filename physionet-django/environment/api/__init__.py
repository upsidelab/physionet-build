from requests import Request
from environment.api.decorators import api_request


@api_request("/user")
def create_cloud_identity(user_id, family_name, given_name):
    json = {"userid": user_id, "familyName": family_name, "givenName": given_name}
    return Request("POST", json=json)


@api_request("/workspace")
def create_workspace(user_id, billing_id, region):
    json = {"userid": user_id, "billingid": billing_id, "region": region}
    return Request("POST", json=json)
