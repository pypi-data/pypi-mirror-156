from datetime import datetime
from typing import Any, ClassVar, List, Optional

try:
    import constants
except ImportError:
    from . import constants

from pydantic import BaseModel


class Registration(BaseModel):
    reg_num: Optional[int]
    first_names: str
    last_name: str
    name_badge: str
    cell: str
    email: str
    dietary: Optional[str]
    disability: Optional[str]
    lion: bool
    timestamp: datetime
    reg_num_string: Optional[str]
    full_name: Optional[str]
    auto_name_badge: Optional[bool]

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.reg_num:
            self.reg_num_string = f"MDC{self.reg_num:03}"
        self.full_name = f"{self.first_names} {self.last_name}"
        if not self.name_badge:
            self.name_badge = self.full_name
            self.auto_name_badge = True
