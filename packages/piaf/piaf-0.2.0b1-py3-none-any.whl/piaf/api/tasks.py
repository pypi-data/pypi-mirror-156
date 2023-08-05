# coding: utf-8
"""A collection of predefined tasks to interact from the WebAPI with a simulation."""
from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List
from uuid import UUID, uuid4

from piaf.agent import AgentState
from piaf.comm import AID, MT_CONVERSATION_ID, ACLMessage, Performative
from piaf.service import AgentCreationDescription, AMSAgentDescription, AMSService

if TYPE_CHECKING:
    from piaf.api.managers import APIAgent


class Task(metaclass=abc.ABCMeta):
    """
    An abstraction of a task.

    Each task gets a unique ID number so a response can later be associated. Concrete class should implement two methods:

    - :meth:`Task.from_json` which creates an instance from a JSON-like structure
    - :meth:`Task.execute` which does the actual work
    """

    @abc.abstractmethod
    @staticmethod
    def from_json(json_repr: Dict[str, Any]) -> Task:
        """
        Unpack the given JSON object into a :class:`Task`.

        :param json_repr: the JSON object
        :return: a :class:`Task` object or one of its subclasses
        """
        raise NotImplementedError()

    def __init__(self) -> None:
        """
        Initialize a new :class:`Task` object.

        It generates a new UUID4 an set it as the task's ID.
        """
        self._id: UUID = uuid4()

    @property
    def id(self) -> UUID:
        """
        Get this task's ID.

        :return: an UUID
        """
        return self._id

    @abc.abstractmethod
    async def execute(self, agent: APIAgent) -> Any:
        """
        Realize the work the task is supposed to do.

        :param agent: the :class:`APIAgent` that is executing the task
        :return: whatever the task returns
        """
        raise NotImplementedError()


@dataclass(frozen=True, eq=True)
class TaskResult:
    """
    A small dataclass that stores a task's execution result.

    This class has three fields:

    - error: stores an exception if the execution failed
    - result: the task's execution result, if any
    - task_id: the task's id this result is linked to

    """

    error: BaseException | None
    result: Any
    task_id: UUID


class CreateAgentTask(Task):
    """
    A task that creates a new agent in the platform.

    Given an :class:`piaf.service.AgentCreationDescription` serialized in a JSON object, this task asks the AMS to create and initialize an agent.

    On a successful execution, the task returns the AID of the created agent.
    """

    @staticmethod
    def from_json(json_repr: Dict[str, Any]) -> CreateAgentTask:
        """
        Create a new :class:`CreateAgentTask` from the given JSON object.

        The object must have the following fields:

        - class_name: qualified name of the agent's class
        - agent_name: short name of the agent
        - args: extra arguments given to the agent's constructor
        - is_service: tell if the agent should have a full access to the platform
        """
        return CreateAgentTask(json_repr)

    def __init__(self, agent: Dict[str, Any]) -> None:
        """Initialize a new :class:`CreateAgentTask` with the given JSON object."""
        super().__init__()
        self.agent = agent

    async def execute(self, agent: APIAgent) -> AID:
        """
        Ask the AMS to create an initialize a new agent in the platform.

        :param agent: the :class:`APIAgent` that executes the request
        :return: the AID of the created agent
        :raise Exception: the AMS refuse to create the agent or fail at it
        """
        req: ACLMessage = (
            ACLMessage.Builder()
            .performative(Performative.REQUEST)
            .conversation_id(str(uuid4()))
            .receiver(AID(f"ams@{agent.aid.hap_name}"))
            .content(
                [
                    AMSService.CREATE_AGENT_FUNC,
                    AgentCreationDescription(
                        self.agent["class_name"],
                        self.agent["agent_name"],
                        self.agent["args"],
                        self.agent["is_service"],
                    ),
                ]
            )
            .build()
        )
        agent.send(req)

        # Wait response
        agree_or_refuse = await agent.receive(MT_CONVERSATION_ID(req.conversation_id))
        if agree_or_refuse.acl_message.performative == Performative.REFUSE:
            raise Exception(agree_or_refuse.acl_message.content)

        # Wait result
        result = await agent.receive(MT_CONVERSATION_ID(req.conversation_id))
        if result.acl_message.performative == Performative.FAILURE:
            raise Exception(result.acl_message.content)

        return result.acl_message.content[1]  # type: ignore


class GetAgentsTask(Task):
    """
    A task that queries the AMS about agents in the platform.

    Two filters are available:

    - state: if set, filters out agent that have a different state from the one provided
    - name: filters out agents that don't have the provided string in their short name

    On a successful execution, the task returns a list of :class:`piaf.service.AMSAgentDescription`.
    """

    @staticmethod
    def from_json(json_repr: Dict[str, Any]) -> GetAgentsTask:
        """
        Creates a new :class:`GetAgentsTask` from the given JSON object.

        It uses only the `filters` field, which must contain two entries:

        - `state`: if not `None`, must be the string representation of one of the constants in :class:`piaf.agent.AgentState`
        - `name`: a string to filter out agents by their short name

        """
        return GetAgentsTask(json_repr["filters"])

    def __init__(self, filters: Dict[str, Any]) -> None:
        """
        Initialize a new :class:`GetAgentsTask` instance.

        :param filters: a JSON object that contains the two required fields
        """
        super().__init__()
        self.filters = filters

    async def execute(self, agent: APIAgent) -> List[AMSAgentDescription]:
        """
        Ask the AMS the list of agents in the platform an apply filters.

        :param agent: the APIAgent executing the task
        :return: a list of :class:`piaf.service.AMSAgentDescription`
        :raise Exception: the AMS refuse to perform the request or fail at it
        """
        req: ACLMessage = (
            ACLMessage.Builder()
            .performative(Performative.REQUEST)
            .conversation_id(str(uuid4()))
            .receiver(AID(f"ams@{agent.aid.hap_name}"))
            .content(
                [
                    AMSService.SEARCH_FUNC,
                    AMSAgentDescription(
                        state=AgentState[self.filters["state"]]
                    ),  # Filter state
                ]
            )
            .build()
        )
        agent.send(req)

        # Wait response
        agree_or_refuse = await agent.receive(MT_CONVERSATION_ID(req.conversation_id))
        if agree_or_refuse.acl_message.performative == Performative.REFUSE:
            raise Exception(agree_or_refuse.acl_message.content)

        # Wait result
        result = await agent.receive(MT_CONVERSATION_ID(req.conversation_id))
        if result.acl_message.performative == Performative.FAILURE:
            raise Exception(result.acl_message.content)

        # Filter using 'name'
        agents: List[AMSAgentDescription] = result.acl_message.content[1]
        return [
            agent for agent in agents if self.filters["name"] in agent.name.short_name
        ]
