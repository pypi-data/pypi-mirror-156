import functools
import logging
from itertools import chain
from typing import Type, TypeVar, Iterable

import boto3
from botocore.exceptions import ClientError
from odd_collector_sdk.domain.adapter import AbstractAdapter
from odd_models.models import DataEntityList
from oddrn_generator.generators import S3Generator

from odd_ge_adapter.domain import Suite, RunResult
from odd_ge_adapter.domain.plugin import S3StoragePlugin
from odd_ge_adapter.error import AccountIdError
from odd_ge_adapter.mappers import map_result, map_suite
from odd_ge_adapter.oddrn import GreatExpectationGenerator

K = TypeVar("K", Suite, RunResult)


class Adapter(AbstractAdapter):
    def __init__(self, config: S3StoragePlugin):
        self._suites_key = config.suites_key
        self._results_key = config.results_key
        self._bucket = config.bucket

        aws_access_key_id = config.aws_access_key_id.get_secret_value()
        aws_secret_access_key = config.aws_secret_access_key.get_secret_value()
        aws_session_token = (
            config.aws_session_token.get_secret_value()
            if config.aws_session_token
            else None
        )

        self._s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=config.aws_region,
        )

        if not config.aws_account_id:
            logging.debug(
                "aws_account_id was not set. Trying to find it using sts account"
            )

            try:
                account_id = boto3.client(
                    "sts",
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_session_token=aws_session_token,
                ).get_caller_identity()["Account"]
            except ClientError as e:
                raise AccountIdError(
                    aws_access_key_id,
                    aws_secret_access_key,
                )
        else:
            account_id = config.aws_account_id

        self._ge_oddrn = GreatExpectationGenerator(
            cloud_settings={
                "account": account_id,
                "region": config.aws_region,
            }
        )
        self._s3_oddrn = S3Generator(
            cloud_settings={
                "account": account_id,
                "region": config.aws_region,
            }
        )

    def get_data_entity_list(self) -> DataEntityList:
        items = list(chain(*self.load_suites(), *self.load_results()))

        return DataEntityList(
            data_source_oddrn=self.get_data_source_oddrn(), items=items
        )

    def get_data_source_oddrn(self) -> str:
        return self._ge_oddrn.get_data_source_oddrn()

    def load_results(self):
        results = self._fetch_list(prefix=self._results_key, cls=RunResult)

        to_data_entity = functools.partial(
            map_result,
            oddrn_generator=self._ge_oddrn,
            s3_oddrn_generator=self._s3_oddrn,
        )

        return map(to_data_entity, results)

    def load_suites(self):
        suites = self._fetch_list(prefix=self._suites_key, cls=Suite)

        to_data_entity = functools.partial(
            map_suite, oddrn_generator=self._ge_oddrn, s3_oddrn_generator=self._s3_oddrn
        )

        return map(to_data_entity, suites)

    def _load_contents(self, key: str) -> str:
        response = self._s3.get_object(Bucket=self._bucket, Key=key)
        return response["Body"].read().decode("utf-8")

    def _fetch_list(self, prefix: str, cls: Type[K]) -> Iterable[K]:
        paginator = self._s3.get_paginator("list_objects_v2")

        responses = list(
            paginator.paginate(Bucket=self._bucket, Prefix=prefix.lstrip("/"))
        )

        contents = [c for r in responses for c in r.get("Contents", [])]
        if len(contents) == 0:
            logging.warning(f"Folder by path {prefix} is an empty")

        json_files = [obj for obj in contents if obj["Key"].endswith(".json")]

        for file in json_files:
            try:
                loaded = self._load_contents(file["Key"])
                model = cls.parse_raw(loaded)
            except Exception as e:
                logging.exception(e)
                continue
            else:
                yield model
