import boto3
import json
from mpi4py import MPI
from bodo_platform_utils.config import WORKSPACE_UUID, REGION, CLOUD_PROVIDER
from bodo_platform_utils.utils_types import CloudProvider


def _get_ssm_parameter(parameter_name):
    ssm_client = boto3.client("ssm", REGION)
    parameters = ssm_client.get_parameters(Names=[parameter_name], WithDecryption=True)
    data = json.loads(parameters["Parameters"][0].get("Value"))
    return data


def _get_ssm_parameter_parallel(parameter_name):
    comm = MPI.COMM_WORLD
    data_or_e = None
    if comm.Get_rank() == 0:
        try:
            data_or_e = _get_ssm_parameter(parameter_name)
        except Exception as e:
            data_or_e = e

    data_or_e = comm.bcast(data_or_e)

    if isinstance(data_or_e, Exception):
        raise data_or_e
    data = data_or_e
    return data


# Users have to use the below helper functions to get the secrets from SSM.

def snowflake_credentials(_parallel=True):
    """
    :param _parallel(Optional) - Defaults to True

    :return: snowflake credentials as JSON
    """
    if CLOUD_PROVIDER == CloudProvider.AWS:
        parameter_name = (
            f"/bodo/workspaces/{WORKSPACE_UUID}/secrets/snowflake_credentials"
        )
        if _parallel:
            return _get_ssm_parameter_parallel(parameter_name)
        else:
            return _get_ssm_parameter(parameter_name)
    elif CLOUD_PROVIDER == CloudProvider.AZURE:
        raise NotImplementedError("This functionality is not supported for Azure.")
    else:
        raise ValueError(f"Unrecognized Cloud Provider: {CLOUD_PROVIDER}")