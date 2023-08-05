# coding: utf-8
"""The mod:`piaf.api.routes` modules defines all routes available in the Web API."""
from __future__ import annotations

import json
from typing import List, Optional
from uuid import uuid4

from async_timeout import timeout
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from piaf.agent import AgentState
from piaf.api.managers import ptf_manager
from piaf.api.models import (
    AgentCreationDescriptionModelIn,
    AgentPlatformModelIn,
    AIDModel,
    AMSAgentDescriptionModelOut,
    ExceptionModel,
)

# V1 router
app_v1 = APIRouter()


@app_v1.post(
    "/platforms",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionModel},
    },
)
async def create_platform(ptf: AgentPlatformModelIn):
    """
    Create a new AgentPlatform with the provided name.

    :param ptf: the platform description
    """
    try:
        await ptf_manager.spawn(ptf)
    except Exception as e:
        return {"details": str(e)}


@app_v1.delete(
    "/platforms",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionModel},
    },
)
async def delete_platform(ptf: AgentPlatformModelIn):
    """
    Stop and delete the desired platform.

    :param ptf: the platform description
    """
    try:
        await ptf_manager.kill(ptf)
    except Exception as e:
        return {"details": str(e)}


@app_v1.get("/platforms", response_model=List[AgentPlatformModelIn])
async def get_platforms():
    """Get all the running platforms this application is aware of."""
    return await ptf_manager.get_all_platforms()


@app_v1.post(
    "/platforms/{name}/agents",
    status_code=status.HTTP_200_OK,
    response_model=AIDModel,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionModel},
    },
)
async def create_agent(name: str, agent: AgentCreationDescriptionModelIn):
    """
    Create and invoke an agent into the specified platform.

    :param name: the platform's name
    :param agent: the description of the agent to create
    :return: an positive reply containing the AID of the created agent or the description o the error
    """
    platforms = await ptf_manager.get_all_platforms()
    if name not in (ptf["name"] for ptf in platforms):
        return JSONResponse(
            content={"details": f"Unknown platform '{name}'"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    pubsub = ptf_manager.db.pubsub(ignore_subscribe_messages=True)
    await pubsub.subscribe(f"channels:{name}:to-api")

    task = {"task_type": "CreateAgentTask", "id": str(uuid4())}
    task.update(agent.dict())
    await ptf_manager.db.publish(f"channels:{name}:from-api", json.dumps(task))

    async with timeout(2):
        async for msg in pubsub.listen():
            response = json.loads(msg["data"])
            if response["id"] == task["id"]:
                del response["id"]
                break

    await pubsub.close()

    return response


@app_v1.get(
    "/platforms/{ptf_name}/agents",
    status_code=status.HTTP_200_OK,
    response_model=List[AMSAgentDescriptionModelOut],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionModel},
    },
)
async def get_agents(
    ptf_name: str, state: Optional[AgentState] = AgentState.ACTIVE, name: str = ""
):
    """
    Retrieve for the given platform all the agents matching the criteria.

    :param ptf_name: the name of the platform
    :param state: (Optional, default to ACTIVE) only take the agents in the given state
    :param name: (Optional, default to "") filter agents to retain only the ones having the given string given in their shortname.
    :return: either a list of agent description or an error message
    """
    platforms = await ptf_manager.get_all_platforms()
    if ptf_name not in (ptf["name"] for ptf in platforms):
        return JSONResponse(
            content={"details": f"Unknown platform '{ptf_name}'"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    pubsub = ptf_manager.db.pubsub(ignore_subscribe_messages=True)
    await pubsub.subscribe(f"channels:{ptf_name}:to-api")

    task = {
        "task_type": "GetAgentsTask",
        "filters": {"state": state.name if state is not None else None, "name": name},
        "id": str(uuid4()),
    }
    await ptf_manager.db.publish(f"channels:{ptf_name}:from-api", json.dumps(task))

    async with timeout(2):
        async for msg in pubsub.listen():
            response = json.loads(msg["data"])
            if response["id"] == task["id"]:
                del response["id"]
                break

    await pubsub.close()

    return response
