#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from torch import monitor


class SourceType(str, Enum):
    UNKNOWN = "<unknown>"
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"


@dataclass
class TorchxEvent:
    """
    The class represents the event produced by ``torchx.runner`` api calls.

    Arguments:
        session: Session id that was used to execute request.
        scheduler: Scheduler that is used to execute request
        api: Api name
        app_id: Unique id that is set by the underlying scheduler
        runcfg: Run config that was used to schedule app.
        source: Type of source the event is generated.
    """

    session: str
    scheduler: str
    api: str
    app_id: Optional[str] = None
    runcfg: Optional[str] = None
    raw_exception: Optional[str] = None
    source: SourceType = SourceType.UNKNOWN

    def __str__(self) -> str:
        return self.serialize()

    @staticmethod
    def deserialize(data: Union[str, "TorchxEvent"]) -> "TorchxEvent":
        if isinstance(data, TorchxEvent):
            return data
        if isinstance(data, str):
            data_dict = json.loads(data)
            if "source" in data_dict:
                # Convert string to enum
                try:
                    data_dict["source"] = SourceType(data_dict["source"])
                except ValueError:
                    data_dict.pop("source", None)

        # pyre-fixme[61]: `data_dict` may not be initialized here.
        return TorchxEvent(**data_dict)

    def serialize(self) -> str:
        return json.dumps(asdict(self))

    # pyre-fixme[11]: Annotation `Event` is not defined as a type.
    def to_monitor_event(self) -> "monitor.Event":
        from torch import monitor

        # pyre-fixme[16]: Module `monitor` has no attribute `Event`.
        return monitor.Event(
            name="torch.runner.Event",
            timestamp=datetime.now(),
            data={k: v for k, v in self.__dict__.items() if v is not None},
        )
