from typing import Optional

from requests import Request

from environment.api.decorators import api_request


@api_request
def create_cloud_identity(
    gcp_user_id: str, given_name: str, family_name: str
) -> Request:
    json = {"userid": gcp_user_id, "givenName": given_name, "familyName": family_name}
    return Request("POST", url="/user", json=json)


@api_request
def get_user_info(gcp_user_id: str) -> Request:
    return Request("GET", url=f"/user/{gcp_user_id}")


@api_request
def create_workspace(gcp_user_id: str, billing_id: str, region: str) -> Request:
    json = {"userid": gcp_user_id, "billingid": billing_id, "region": region}
    return Request("POST", url="/onetimeplatformsetup", json=json)


@api_request
def get_workspace_details(gcp_user_id: str, region: str) -> Request:
    return Request("GET", url=f"/workspace/{gcp_user_id}/{region}")


@api_request
def get_workspace_list(gcp_user_id: str) -> Request:
    return Request("GET", url=f"/workspace/list/{gcp_user_id}")


@api_request
def stop_workbench(gcp_user_id: str, workbench_id: str, region: str) -> Request:
    params = {"userid": gcp_user_id, "id": workbench_id, "region": region}
    return Request("PUT", url="/workbench/stop", params=params)


@api_request
def start_workbench(gcp_user_id: str, workbench_id: str, region: str) -> Request:
    params = {"userid": gcp_user_id, "id": workbench_id, "region": region}
    return Request("PUT", url="/workbench/start", params=params)


@api_request
def change_workbench_instance_type(
    gcp_user_id: str, workbench_id: str, region: str, new_instance_type: str
) -> Request:
    params = {
        "userid": gcp_user_id,
        "id": workbench_id,
        "region": region,
        "machinetype": new_instance_type,
    }
    return Request("PUT", url="/workbench/update", params=params)


@api_request
def delete_workbench(gcp_user_id: str, workbench_id: str, region: str) -> Request:
    params = {"userid": gcp_user_id, "id": workbench_id, "region": region}
    return Request("DELETE", url="/workbench", params=params)


@api_request
def create_workbench(
    gcp_user_id: str,
    region: str,
    environment_type: str,
    instance_type: str,
    group_granting_data_access: str,
    bucket_name: Optional[str] = None,
    persistent_disk: Optional[str] = None,
    vm_image: Optional[str] = None,
):
    json = {
        "userid": gcp_user_id,
        "region": region,
        "type": environment_type,
        "machinetype": instance_type,
        "group_granting_data_access": group_granting_data_access,
        "bucketname": bucket_name,
        "persistentdisk": persistent_disk,
        "vmimage": vm_image,
    }
    json_without_empty_values = {
        key: val for key, val in json.items() if val is not None
    }
    return Request("POST", url="/workbench", json=json_without_empty_values)
