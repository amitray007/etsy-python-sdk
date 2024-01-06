from typing import Any, List, Optional

from etsy_python.v3.models.Request import Request


class FileRequest(Request):
    def __init__(
        self,
        nullable: Optional[List[str]] = None,
        mandatory: Optional[List[str]] = None,
    ) -> None:
        self.file: Any = self.file if self.file is not None else None
        self.data: Any = self.data if self.data is not None else None
        super().__init__(nullable=nullable, mandatory=mandatory)
