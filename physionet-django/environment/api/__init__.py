from requests import Request
from environment.api.decorators import api_request


@api_request
def create_cloud_identity(gcp_user_id, family_name, given_name):
    json = {"userid": gcp_user_id, "familyName": family_name, "givenName": given_name}
    return Request("POST", url="/user", json=json)


@api_request
def get_workspace_list(gcp_user_id):
    return Request("GET", url=f"/workspace/list/{gcp_user_id}")
