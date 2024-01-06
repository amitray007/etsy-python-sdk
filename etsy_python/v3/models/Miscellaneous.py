from typing import List, Optional

from etsy_python.v3.models.Request import Request


class GetTokenScopes(Request):
    nullable: List[str] = []
    mandatory: List[str] = ["token"]

    def __init__(self, token: Optional[str] = None):
        self.token = token

        super().__init__(
            nullable=GetTokenScopes.nullable, mandatory=GetTokenScopes.mandatory
        )
