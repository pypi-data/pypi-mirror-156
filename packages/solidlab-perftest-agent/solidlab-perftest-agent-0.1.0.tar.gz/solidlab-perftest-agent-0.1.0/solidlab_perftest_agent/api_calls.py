import logging
from typing import Optional, Any, List

import aiohttp
from aiohttp import ClientSession, ClientResponse
from imecilabt_utils import datetime_now
from solidlab_perftest_common import status
from solidlab_perftest_common.agent import (
    AgentCommand,
    AgentCommandResult,
    AgentCommandResultStatus,
    Agent,
    AgentCommandFull,
)
from solidlab_perftest_common.content_types import SolidLabContentType
from solidlab_perftest_common.pagination import Page

from solidlab_perftest_agent.config import Config


class ApiError(Exception):
    def __init__(
        self,
        message: str,
        response: Optional[ClientResponse],
        *,
        response_body: Optional[Any] = None,
    ) -> None:
        super().__init__()
        self.message = message
        self.response = response
        self.response_body = response_body
        if self.response and not response_body:
            try:
                self.response_body = (
                    await response.text()
                    if response.content_type == "text/plain"
                    else await response.json()
                )
            except:
                pass  # ignore error fetching body of response

    def __str__(self) -> str:
        if self.response:
            return f"ApiError({self.message}, status={self.response.status}, body={self.response_body})"
        else:
            return f"ApiError({self.message})"


class Api:
    def __init__(self, config: Config):
        self.config = config
        self.agent_url = f"{self.config.api_endpoint}testenv/{self.config.test_env_id}/agent/{self.config.machine_id}"
        self.session: ClientSession = aiohttp.ClientSession(
            # auth=BasicAuth(
            #     login=get_settings().GITHUB_USER, password=get_settings().GITHUB_PASS
            # )
            headers={
                "Solidlab-PerfTest-Auth": config.auth_token,
                "Accept": "application/json",
            },
        )

    async def agent_hello(self):
        async with self.session as session:
            async with session.put(
                self.agent_url,
                json=Agent(
                    id=self.config.test_env_id,
                    machineId=self.config.test_env_id,
                    last_active=datetime_now(),
                    active=True,
                ).dict(),
                headers={"Content-Type": SolidLabContentType.AGENT_STATUS.value},
            ) as response:
                if not response.ok:
                    raise ApiError("Failed to say hello", response)

    async def agent_goodbye(self):
        async with self.session as session:
            async with session.put(
                self.agent_url,
                json=Agent(
                    id=self.config.test_env_id,
                    machineId=self.config.test_env_id,
                    last_active=datetime_now(),
                    active=False,
                ).dict(),
                headers={"Content-Type": SolidLabContentType.AGENT_STATUS.value},
            ) as response:
                if not response.ok:
                    raise ApiError("Failed to say goodbye", response)

    async def request_commands(self) -> List[AgentCommand]:
        url = f"{self.agent_url}/commands"
        async with self.session as session:
            async with session.get(
                self.agent_url,
                headers={"Accept": SolidLabContentType.AGENT_COMMAND.value},
                params={"finished": True, "wait": 5.0},
            ) as response:
                if not response.ok:
                    raise ApiError("Failed to fetch command", response)
                if response.status == status.HTTP_204_NO_CONTENT:
                    return []
                resp_obj = await response.json()
                # This returns a dict version of Page[AgentCommandFull]
                if not resp_obj:
                    return []
                if not isinstance(resp_obj, dict) or "total" not in resp_obj:
                    raise ApiError(
                        f"Got unexpected response to {url}",
                        response,
                        response_body=resp_obj,
                    )
                bound_page_class = Page[AgentCommandFull]
                try:
                    page = bound_page_class.parse_obj(resp_obj)
                except:
                    raise ApiError(
                        f"Got unexpected response to {url}",
                        response,
                        response_body=resp_obj,
                    )
                # TODO: handle that this only returns first commands of many, if page.total > page.size
                #       (but that can probably be ignored: new commands will just be requested later)
                return [AgentCommand.parse_obj(ac) for ac in page.items]
        return []

    async def report_command_status(
        self,
        command: AgentCommand,
        status: AgentCommandResultStatus,
        return_value: Optional[int] = None,
        error_msg: Optional[str] = None,
        trace: Optional[str] = None,
        debug_msg: Optional[str] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
    ) -> None:
        await self.report_command_result(
            AgentCommandResult(
                commandId=command.id,
                status=status,
                return_value=return_value,
                error_msg=error_msg,
                trace=trace,
                debug_msg=debug_msg,
                stdout=stdout,
                stderr=stderr,
            )
        )

    async def report_command_result(self, res: AgentCommandResult) -> None:
        url = f"{self.agent_url}/commands/{res.command_id}/result"
        async with self.session as session:
            async with session.put(
                url,
                json=res.dict(),
                headers={
                    "Content-Type": SolidLabContentType.AGENT_COMMAND_RESULT.value
                },
            ) as response:
                if not response.ok:
                    raise ApiError("Failed to say goodbye", response)
