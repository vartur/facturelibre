from pydantic import BaseModel, Field


class RcProInfo(BaseModel):
    """
    A class representing the RC PRO (professional liability insurance) details.

    Attributes:
        name (str): The name of the insurance company providing the RC PRO coverage.
        address_line_1 (str): The first part of the insurance company's address, including street number and name.
        address_line_2 (str): The second part of the insurance company's address, including postal code and city.
        geographical_coverage (str): The geographical region covered by the insurance policy.

    """

    name: str = Field(..., description="The name of the insurance company")
    address_line_1: str = Field(...,
                                description="The first part of the insurance company's address (number and street name")
    address_line_2: str = Field(...,
                                description="The second part of the insurance company's address (postal code and city)")
    geographical_coverage: str = Field(..., description="The geographical coverage of the insurance policy")
