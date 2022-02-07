from pydantic import BaseModel


class BillingAccountRequestData(BaseModel):
    familyname: str
    givenname: str
    userid: str


class BillingAccountResponseData(BaseModel):
    billingaccount_url: str
    url: str
    email_id: str
    password: str
    status: str


class WorkspaceRequestData(BaseModel):
    userid: str
    type: str
    machinetype: str
    # use enum in the future
    region: str
    dataset: str
    bucketname: str
