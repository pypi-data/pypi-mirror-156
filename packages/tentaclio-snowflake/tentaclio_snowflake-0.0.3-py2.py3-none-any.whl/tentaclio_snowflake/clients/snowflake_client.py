from typing import Union

from tentaclio import urls
from tentaclio.clients import sqla_client


class SnowflakeClient(sqla_client.SQLAlchemyClient):
    def __init__(
        self, url: Union[str, urls.URL], execution_options: dict = None, connect_args: dict = None
    ):
        super().__init__(url=url, execution_options=execution_options, connect_args=connect_args)
