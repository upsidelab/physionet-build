from requests import Request

from environment.api.decorators import api_request


@api_request
def create_cloud_identity(
    gcp_user_id: str, family_name: str, given_name: str
) -> Request:
    json = {"userid": gcp_user_id, "familyName": family_name, "givenName": given_name}
    return Request("POST", url="/user", json=json)


@api_request
def get_workspace_list(gcp_user_id: str) -> Request:
    return Request("GET", url=f"/workspace/list/{gcp_user_id}")


@api_request
def workspace_creation(gcp_user_id: str, billing_id: str, region: str ) -> Request:
    json = {"userid": gcp_user_id, "billingid": billing_id, "region": region}
    return Request("POST", url="/workspace", json=json)
