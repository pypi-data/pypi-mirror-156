"""MQTT information class."""
import time
from typing import Mapping

import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessageInfo

from ..exceptions import MQTTException
from ..helpers import get_logger
from .landroid_class import LDict

_LOGGER = get_logger("mqtt")


class MQTTMsgType(LDict):
    """Define specific message type data."""

    def __init__(self):
        super().__init__()

        self["in"] = 0
        self["out"] = 0


class MQTTMessages(LDict):
    """Messages class."""

    def __init__(self):
        super().__init__()

        self["raw"] = MQTTMsgType()
        self["filtered"] = MQTTMsgType()


class MQTTTopics(LDict):
    """Topics class."""

    def __init__(self):
        super().__init__()

        self["in"] = None
        self["out"] = None


class Command:
    """Landroid Cloud commands."""

    START = 1
    PAUSE = 2
    HOME = 3
    ZONETRAINING = 4
    LOCK = 5
    UNLOCK = 6
    RESTART = 7
    PAUSE_OVER_WIRE = 8
    SAFEHOME = 9


class MQTTData(LDict):
    """Class for handling MQTT information."""

    __topics: MQTTTopics = MQTTTopics()
    __logger_enabled: bool = False

    def __init__(self):
        """Init MQTT info class."""
        super().__init__()
        self["messages"] = MQTTMessages()
        self["endpoint"] = None
        self["registered"] = None
        self["connected"] = False

    @property
    def logger(self) -> bool:
        """Return if logger is enabled or not."""
        return self.__logger_enabled

    @logger.setter
    def logger(self, value: bool) -> None:
        """Set logger state."""
        self.__logger_enabled = value

    @property
    def topics(self) -> dict:
        """Return topics dict."""
        return self.__topics

    @topics.setter
    def topics(self, value: dict) -> None:
        """Set topics values."""
        for k, v in value.items() if isinstance(value, Mapping) else value:
            self.__topics.update({k: v})


class MQTT(mqtt.Client, LDict):
    """Full MQTT handler class."""

    def __init__(
        self,
        master=None,
        clean_session=None,
        userdata=None,
        protocol=mqtt.MQTTv311,
        transport="tcp",
        reconnect_on_failure=True,
    ):
        if isinstance(master, type(None)):
            return

        super().__init__(
            master._worx_mqtt_client_id,
            clean_session,
            userdata,
            protocol,
            transport,
            reconnect_on_failure,
        )

        self.topics = master.mqttdata.topics
        self.name = master.name
        self.master = master

        master.mqttdata["connected"] = False

    @property
    def connected(self) -> bool:
        """Return connection state."""
        return self.master.mqttdata["connected"]

    @connected.setter
    def connected(self, state: bool) -> None:
        """Set connected flag."""
        self.master.mqttdata["connected"] = state

    def send(
        self,
        data: str = "{}",
        qos: int = 0,
        retain: bool = False,
        force: bool = False,
    ) -> MQTTMessageInfo:
        """Send Landroid cloud message to API endpoint."""
        topic = self.topics["in"]
        _LOGGER.debug("Sending %s to %s on %s", data, self.name, topic)
        if not self.connected and not force:
            _LOGGER.error(
                "MQTT server was not connected, can't send message to %s", self.name
            )
            raise MQTTException("MQTT not connected")

        try:
            status = self.publish(topic, data, qos, retain)
            _LOGGER.debug("Awaiting message to be published to %s", self.name)
            while not status.is_published:
                time.sleep(0.1)
            return status
        except ValueError as exc:
            _LOGGER.error(
                "MQTT queue for %s was full, message %s was not sent!", self.name, data
            )
        except RuntimeError as exc:
            _LOGGER.error(
                "MQTT error while sending message %s to %s.\n%s", data, self.name, exc
            )
        except Exception as exc:
            _LOGGER.error("MQTT error %s to %s.\n%s", data, self.name, exc)

    def command(self, action: Command) -> MQTTMessageInfo:
        """Send command to device."""
        cmd = '"cmd":{}'.format(action)
        cmd = "{" + cmd + "}"
        return self.send(cmd)
