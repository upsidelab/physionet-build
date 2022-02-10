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
def create_workbench(
    gcp_user_id,
    region,
    environment_type,
    instance_type,
    dataset,
    bucket_name=None,
    persistent_disk=None,
    vm_image=None,
):
    json = {
        "userid": gcp_user_id,
        "region": region,
        "type": environment_type,
        "machinetype": instance_type,
        "dataset": dataset,
        "bucketname": bucket_name,
        "persistentdisk": persistent_disk,
        "vmimage": vm_image,
    }
    return Request("POST", url="/workbench", json=json)
