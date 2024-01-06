from typing import List, Optional

from etsy_python.v3.models.Request import Request


class ConsolidateShopReturnPoliciesRequest(Request):
    nullable: List[str] = []
    mandatory: List[str] = [
        "source_return_policy_id",
        "destination_return_policy_id",
    ]

    def __init__(
        self, source_return_policy_id: int, destination_return_policy_id: int
    ) -> None:
        self.source_return_policy_id = source_return_policy_id
        self.destination_return_policy_id = destination_return_policy_id

        super().__init__(
            nullable=ConsolidateShopReturnPoliciesRequest.nullable,
            mandatory=ConsolidateShopReturnPoliciesRequest.mandatory,
        )


class CreateShopReturnPolicyRequest(Request):
    nullable: List[str] = ["return_deadline"]
    mandatory: List[str] = [
        "accepts_returns",
        "accepts_exchanges",
    ]

    def __init__(
        self,
        accepts_returns: bool,
        accepts_exchanges: bool,
        return_deadline: Optional[int] = None,
    ) -> None:
        self.accepts_returns = accepts_returns
        self.accepts_exchanges = accepts_exchanges
        self.return_deadline = return_deadline

        super().__init__(
            nullable=CreateShopReturnPolicyRequest.nullable,
            mandatory=CreateShopReturnPolicyRequest.mandatory,
        )


class UpdateShopReturnPolicyRequest(Request):
    nullable: List[str] = ["return_deadline"]
    mandatory: List[str] = [
        "accepts_returns",
        "accepts_exchanges",
    ]

    def __init__(
        self,
        accepts_returns: bool,
        accepts_exchanges: bool,
        return_deadline: Optional[int] = None,
    ) -> None:
        self.accepts_returns = accepts_returns
        self.accepts_exchanges = accepts_exchanges
        self.return_deadline = return_deadline

        super().__init__(
            nullable=UpdateShopReturnPolicyRequest.nullable,
            mandatory=UpdateShopReturnPolicyRequest.mandatory,
        )
