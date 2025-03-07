import libs as libs
import logging
from typing import Any, Dict

from splunkz import modularinput

logger = logging.getLogger(__name__)


def stream_events(
    config_name: str,
    parameters: Dict[str, Any],
    execution: modularinput.ExecutionContext,
    eventwriter: modularinput.EventWriter,
    checkpointer: modularinput.Checkpointer,
):
    pass


modular_input = modularinput.ModularInput(
    arguments=[],
    stream_events=stream_events,
    script_path=__file__,
)

if __name__ == "__main__":
    modular_input.execute_and_exit()
