from ninja.errors import HttpError
from ddpui.models.org_user import Org, OrgUser
from ddpui.models.org import OrgDataFlow, OrgPrefectBlock, OrgWarehouse
from ddpui.ddpairbyte import airbyte_service
from ddpui.ddpprefect import prefect_service
from ddpui.ddpprefect import AIRBYTESERVER, AIRBYTECONNECTION, SHELLOPERATION
from ddpui.ddpdbt import dbt_service
from ddpui.utils import secretsmanager

from ddpui.utils.ddp_logger import logger


def delete_prefect_deployments(org: Org):  # skipcq: PYL-R0201
    """fetches and deletes every prefect deployment for this org"""
    logger.info("=========== OrgDataFlow ===========")
    for dataflow in OrgDataFlow.objects.filter(org=org):
        logger.info("%s %s", dataflow.deployment_id, dataflow.connection_id)
        try:
            prefect_service.delete_deployment_by_id(dataflow.deployment_id)
        except HttpError:
            pass
        dataflow.delete()


def delete_prefect_shell_blocks(org: Org):  # skipcq: PYL-R0201
    """fetches and deletes all prefect blocks for this org"""
    logger.info("=========== OrgPrefectBlock: Shell Operations ===========")
    for block in OrgPrefectBlock.objects.filter(org=org, block_type=SHELLOPERATION):
        logger.info(
            "%s %s %s",
            block.block_name,
            block.display_name,
            block.command,
        )
        prefect_service.delete_shell_block(block.block_id)
        block.delete()


def delete_dbt_workspace(org: Org):  # skipcq: PYL-R0201
    """deletes the dbt workspace"""
    dbt_service.delete_dbt_workspace(org)


def delete_airbyte_workspace(org: Org):  # skipcq: PYL-R0201
    """
    deletes airbyte sources, destinations, connections
    deletes airbyte server and connection blocks in prefect
    """
    logger.info("=========== OrgPrefectBlock: Airbyte Connections ===========")
    for block in OrgPrefectBlock.objects.filter(org=org, block_type=AIRBYTECONNECTION):
        logger.info(
            "%s %s %s %s %s",
            block.block_name,
            block.block_type,
            block.display_name,
            block.dbt_target_schema,
            block.command,
        )
        prefect_service.delete_airbyte_connection_block(block.block_id)
        block.delete()

    logger.info("=========== OrgPrefectBlock: Airbyte Server(s) ===========")
    for block in OrgPrefectBlock.objects.filter(org=org, block_type=AIRBYTESERVER):
        logger.info(
            "%s %s %s %s %s",
            block.block_name,
            block.block_type,
            block.display_name,
            block.dbt_target_schema,
            block.command,
        )
        prefect_service.delete_airbyte_server_block(block.block_id)
        block.delete()

    for connection in airbyte_service.get_connections(org.airbyte_workspace_id)[
        "connections"
    ]:
        logger.info("deleting connection in Airbyte " + connection["connectionId"])
        airbyte_service.delete_connection(
            org.airbyte_workspace_id, connection["connectionId"]
        )

    for destination in airbyte_service.get_destinations(org.airbyte_workspace_id)[
        "destinations"
    ]:
        logger.info("deleting destination in Airbyte " + destination["destinationId"])
        airbyte_service.delete_destination(
            org.airbyte_workspace_id, destination["destinationId"]
        )

    for source in airbyte_service.get_sources(org.airbyte_workspace_id)["sources"]:
        logger.info("deleting source in Airbyte " + source["sourceId"])
        airbyte_service.delete_source(org.airbyte_workspace_id, source["sourceId"])

    for warehouse in OrgWarehouse.objects.filter(org=org):
        secretsmanager.delete_warehouse_credentials(warehouse)
        warehouse.delete()

    airbyte_service.delete_workspace(org.airbyte_workspace_id)


def delete_orgusers(org: Org):  # skipcq: PYL-R0201
    """delete all login users"""
    for orguser in OrgUser.objects.filter(org=org):
        orguser.user.delete()
        # this deletes the orguser as well via CASCADE


def delete_one_org(org: Org, yes_really: bool):
    """delete one org"""
    logger.info(
        "OrgName: %s   Airbyte workspace ID: %s",
        org.name,
        org.airbyte_workspace_id,
    )
    if yes_really:
        delete_prefect_deployments(org)
        delete_dbt_workspace(org)
        if org.airbyte_workspace_id:
            delete_airbyte_workspace(org)
        delete_prefect_shell_blocks(org)
        delete_orgusers(org)
        org.delete()
