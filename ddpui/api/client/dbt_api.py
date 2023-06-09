import os
from pathlib import Path

from ninja import NinjaAPI
from ninja.errors import HttpError

from ninja.errors import ValidationError
from ninja.responses import Response
from pydantic.error_wrappers import ValidationError as PydanticValidationError

from ddpui import auth
from ddpui.ddpprefect.schema import OrgDbtSchema
from ddpui.models.org_user import OrgUserResponse
from ddpui.utils.helpers import runcmd
from ddpui.celeryworkers.tasks import setup_dbtworkspace
from ddpui.ddpprefect import prefect_service
from ddpui.ddpprefect import DBTCORE
from ddpui.ddpdbt import dbt_service

dbtapi = NinjaAPI(urls_namespace="dbt")


@dbtapi.exception_handler(ValidationError)
def ninja_validation_error_handler(request, exc):  # pylint: disable=unused-argument
    """
    Handle any ninja validation errors raised in the apis
    These are raised during request payload validation
    exc.errors is correct
    """
    return Response({"detail": exc.errors}, status=422)


@dbtapi.exception_handler(PydanticValidationError)
def pydantic_validation_error_handler(
    request, exc: PydanticValidationError
):  # pylint: disable=unused-argument
    """
    Handle any pydantic errors raised in the apis
    These are raised during response payload validation
    exc.errors() is correct
    """
    return Response({"detail": exc.errors()}, status=500)


@dbtapi.exception_handler(Exception)
def ninja_default_error_handler(
    request, exc: Exception
):  # pylint: disable=unused-argument # skipcq PYL-W0613
    """Handle any other exception raised in the apis"""
    return Response({"detail": "something went wrong"}, status=500)


@dbtapi.post("/workspace/", auth=auth.CanManagePipelines())
def post_dbt_workspace(request, payload: OrgDbtSchema):
    """Setup the client git repo and install a virtual env inside it to run dbt"""
    orguser = request.orguser
    org = orguser.org
    if org.dbt is not None:
        org.dbt.delete()
        org.dbt = None
        org.save()

    task = setup_dbtworkspace.delay(org.id, payload.dict())

    return {"task_id": task.id}


@dbtapi.delete("/workspace/", response=OrgUserResponse, auth=auth.CanManagePipelines())
def dbt_delete(request):
    """Delete the dbt workspace and project repo created"""
    orguser = request.orguser
    if orguser.org is None:
        raise HttpError(400, "create an organization first")

    dbt_service.delete_dbt_workspace(orguser.org)

    return OrgUserResponse.from_orguser(orguser)


@dbtapi.get("/dbt_workspace", auth=auth.CanManagePipelines())
def get_dbt_workspace(request):
    """return details of the dbt workspace for this org"""
    orguser = request.orguser
    if orguser.org.dbt is None:
        return {"error": "no dbt workspace has been configured"}

    return {
        "gitrepo_url": orguser.org.dbt.gitrepo_url,
        "target_type": orguser.org.dbt.target_type,
        "default_schema": orguser.org.dbt.default_schema,
    }


@dbtapi.post("/git_pull/", auth=auth.CanManagePipelines())
def post_dbt_git_pull(request):
    """Pull the dbt repo from github for the organization"""
    orguser = request.orguser
    if orguser.org.dbt is None:
        raise HttpError(400, "dbt is not configured for this client")

    project_dir = Path(os.getenv("CLIENTDBT_ROOT")) / orguser.org.slug
    if not os.path.exists(project_dir):
        raise HttpError(400, "create the dbt env first")

    try:
        runcmd("git pull", project_dir / "dbtrepo")
    except Exception as error:
        raise HttpError(
            500, f"git pull failed in {str(project_dir / 'dbtrepo')}"
        ) from error

    return {"success": True}
