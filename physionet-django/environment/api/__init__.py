from requests import Request
from environment.api.decorators import api_request


@api_request("/user")
def create_cloud_identity(gcp_user_id, family_name, given_name):
    json = {"userid": gcp_user_id, "familyName": family_name, "givenName": given_name}
    return Request("POST", json=json)


@api_request("/workbench")
def create_workbench(
    user_id,
    region,
    environment_type,
    instance_type,
    bucket_name,
    persistent_disk,
    vm_image,
):
    json = {
        "userid": user_id,
        "region": region,
        "type": environment_type,
        "machinetype": instance_type,
        "bucketname": bucket_name,
        "persistentdisk": persistent_disk,
        "vmimage": vm_image,
    }
    return Request("POST", json=json)
