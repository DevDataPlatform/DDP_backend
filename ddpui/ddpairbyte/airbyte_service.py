import os
import requests

from dotenv import load_dotenv
from ddpui.ddpairbyte import schema

load_dotenv()


def abreq(endpoint, req=None):
    """Docstring"""
    abhost = os.getenv("AIRBYTE_SERVER_HOST")
    abport = os.getenv("AIRBYTE_SERVER_PORT")
    abver = os.getenv("AIRBYTE_SERVER_APIVER")
    token = os.getenv("AIRBYTE_API_TOKEN")

    res = requests.post(
        f"http://{abhost}:{abport}/api/{abver}/{endpoint}",
        headers={"Authorization": f"Basic {token}"},
        json=req,
    )
    return res.json()


def get_workspaces():
    """Docstring"""
    return abreq("workspaces/list")


def get_workspace(workspace_id):
    """Docstring"""
    return abreq("workspaces/get", {"workspaceId": workspace_id})


def set_workspace_name(workspace_id, name):
    """Docstring"""
    abreq("workspaces/update_name", {"workspaceId": workspace_id, "name": name})


def create_workspace(name):
    """Docstring"""
    res = abreq("workspaces/create", {"name": name})
    if "workspaceId" not in res:
        raise Exception(res)
    return res


def get_source_definitions(workspace_id, **kwargs):
    """Docstring"""
    res = abreq("source_definitions/list_for_workspace", {"workspaceId": workspace_id})
    if "sourceDefinitions" not in res:
        raise Exception(res)
    return res["sourceDefinitions"]


def get_source_definition_specification(workspace_id, sourcedef_id):
    """Docstring"""
    res = abreq(
        "source_definition_specifications/get",
        {"sourceDefinitionId": sourcedef_id, "workspaceId": workspace_id},
    )
    if "connectionSpecification" not in res:
        raise Exception(res)
    return res["connectionSpecification"]


def get_sources(workspace_id):
    """Docstring"""
    res = abreq("sources/list", {"workspaceId": workspace_id})
    if "sources" not in res:
        raise Exception(res)
    return res["sources"]


def get_source(workspace_id, source_id):
    """Docstring"""
    res = abreq("sources/get", {"sourceId": source_id})
    if "sourceId" not in res:
        raise Exception(res)
    return res


def create_source(workspace_id, name, sourcedef_id, config):
    """Docstring"""
    res = abreq(
        "sources/create",
        {
            "workspaceId": workspace_id,
            "name": name,
            "sourceDefinitionId": sourcedef_id,
            "connectionConfiguration": config,
        },
    )
    if "sourceId" not in res:
        raise Exception(res)
    return res


def check_source_connection(workspace_id, source_id):
    """Docstring"""
    res = abreq("sources/check_connection", {"sourceId": source_id})
    # {
    #   'status': 'succeeded',
    #   'jobInfo': {
    #     'id': 'ecd78210-5eaa-4a70-89ad-af1d9bc7c7f2',
    #     'configType': 'check_connection_source',
    #     'configId': 'Optional[decd338e-5647-4c0b-adf4-da0e75f5a750]',
    #     'createdAt': 1678891375849,
    #     'endedAt': 1678891403356,
    #     'succeeded': True,
    #     'connectorConfigurationUpdated': False,
    #     'logs': {'logLines': [str]}
    #   }
    # }
    return res


def get_source_schema_catalog(workspace_id, source_id):
    """Docstring"""
    res = abreq("sources/discover_schema", {"sourceId": source_id})
    if "catalog" not in res:
        raise Exception(res)
    return res


def get_destination_definitions(workspace_id, **kwargs):
    """Docstring"""
    res = abreq(
        "destination_definitions/list_for_workspace", {"workspaceId": workspace_id}
    )
    if "destinationDefinitions" not in res:
        raise Exception(res)
    return res["destinationDefinitions"]


def get_destination_definition_specification(workspace_id, destinationdef_id):
    """Docstring"""
    res = abreq(
        "destination_definition_specifications/get",
        {"destinationDefinitionId": destinationdef_id, "workspaceId": workspace_id},
    )
    if "connectionSpecification" not in res:
        raise Exception(res)
    return res["connectionSpecification"]


def get_destinations(workspace_id):
    """Docstring"""
    res = abreq("destinations/list", {"workspaceId": workspace_id})
    if "destinations" not in res:
        raise Exception(res)
    return res["destinations"]


def get_destination(workspace_id, destination_id):
    """Docstring"""
    res = abreq("destinations/get", {"destinationId": destination_id})
    if "destinationId" not in res:
        raise Exception(res)
    return res


def create_destination(workspace_id, name, destinationdef_id, config):
    """Docstring"""
    res = abreq(
        "destinations/create",
        {
            "workspaceId": workspace_id,
            "name": name,
            "destinationDefinitionId": destinationdef_id,
            "connectionConfiguration": config,
        },
    )
    if "destinationId" not in res:
        raise Exception(res)
    return res


def check_destination_connection(workspace_id, destination_id):
    """Docstring"""
    res = abreq("destinations/check_connection", {"destinationId": destination_id})
    return res


def get_connections(workspace_id):
    """Docstring"""
    res = abreq("connections/list", {"workspaceId": workspace_id})
    if "connections" not in res:
        raise Exception(res)
    return res["connections"]


def get_connection(workspace_id, connection_id):
    """Docstring"""
    res = abreq("connections/get", {"connectionId": connection_id})
    if "connectionId" not in res:
        raise Exception(res)
    return res


def create_connection(workspace_id, connection_info: schema.AirbyteConnectionCreate):
    """Docstring"""
    if len(connection_info.streamnames) == 0:
        raise Exception("must specify stream names")

    sourceschemacatalog = get_source_schema_catalog(
        workspace_id, connection_info.source_id
    )

    payload = {
        "sourceId": connection_info.source_id,
        "destinationId": connection_info.destination_id,
        "sourceCatalogId": sourceschemacatalog["catalogId"],
        "syncCatalog": {
            "streams": [
                # <== we're going to put the stream configs in here in the next step below
            ]
        },
        "status": "active",
        "prefix": "",
        "namespaceDefinition": "destination",
        "namespaceFormat": "${SOURCE_NAMESPACE}",
        "nonBreakingChangesPreference": "ignore",
        "scheduleType": "manual",
        "geography": "auto",
        "name": connection_info.name,
        "operations": [
            {
                "name": "Normalization",
                "workspaceId": workspace_id,
                "operatorConfiguration": {
                    "operatorType": "normalization",
                    "normalization": {"option": "basic"},
                },
            }
        ],
    }

    # one stream per table
    for schema_cat in sourceschemacatalog["catalog"]["streams"]:
        if schema_cat["stream"]["name"] in connection_info.streamnames:
            # set schema_cat['config']['syncMode'] from schema_cat['stream']['supportedSyncModes'] here
            payload["syncCatalog"]["streams"].append(schema_cat)

    res = abreq("connections/create", payload)
    if "connectionId" not in res:
        raise Exception(res)
    return res


def sync_connection(workspace_id, connection_id):
    """Docstring"""
    res = abreq("connections/sync", {"connectionId": connection_id})
    return res