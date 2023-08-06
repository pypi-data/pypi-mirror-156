"""
Fxiaoke object hooks

create connections with extra json:
{"app_id":"", "app_secret":"", "permanent_code":"", "open_user_id":""}
"""
import sys
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Union

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from cached_property import cached_property

from airflow.exceptions import AirflowException
from airflow.hooks.base import BaseHook
from fxiaoke.api import FxiaokeApi
from fxiaoke.query import queryObj as FxiaokeObj


class FxiaokeHooks(BaseHook):
    """
    Hooks for Fxiaoke CRM API
    .. seealso::
        For more information on the fxiaoke CRM API, take a look at the API docs:
        https://open.fxiaoke.com/wiki.html
    """
    conn_name_attr = 'fxiaoke_conn_id'
    default_conn_name = 'fxiaoke_default'
    hook_name = 'Fxiaoke Hooks'

    def __init__(
        self,
        fxiaoke_conn_id: str = default_conn_name,
        api_version: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.fxiaoke_conn_id = fxiaoke_conn_id
        self.api_version = api_version
        self.client_required_fields = [
            "app_id", "app_secret", "permanent_code", "open_user_id"]

    def _get_service(self) -> FxiaokeApi:
        """Returns Facebook Ads Client using a service account"""
        config = self.fxiaoke_config
        return FxiaokeApi.init(
            app_id=config["app_id"],
            app_secret=config["app_secret"],
            permanent_code=config["permanent_code"],
            open_user_id=config["open_user_id"],
            api_version=self.api_version,
        )

    @cached_property
    def fxiaoke_config(self) -> Dict:
        """
        Gets Fxiaoke connection from meta db and sets
        fxiaoke_config attribute with returned config file
        """
        self.log.info("Fetching fb connection: %s", self.facebook_conn_id)
        conn = self.get_connection(self.facebook_conn_id)
        config = conn.extra_dejson
        missing_keys = self.client_required_fields - config.keys()
        if missing_keys:
            message = f"{missing_keys} fields are missing"
            raise AirflowException(message)
        return config

    def list_object(
        self,
        object_name: str,
        ds_start_ms: int,
        ds_end_ms: int,
        filter_fileds: str = 'last_modified_time',
        offset: int = 0,
        limit: int = 100,
    ) -> iter:
        api = self._get_service()
        obj = FxiaokeObj(api)
        return obj.api_get(
            dataObjectApiName=object_name, filters=[{
                'field_name': filter_fileds,
                'field_values': [ds_start_ms, ds_end_ms],
                'operator': 'BETWEEN',
            }],
            limit=limit,
            offset=offset
        )
