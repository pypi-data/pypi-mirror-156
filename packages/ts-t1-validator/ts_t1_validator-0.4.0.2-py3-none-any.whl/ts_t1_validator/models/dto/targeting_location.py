from typing import List

from ts_t1_validator.models.enums.location_type import LocationTypeEnum


class TargetingLocationDTO:
    def __init__(self, location_type: LocationTypeEnum, included: List[int], excluded: List[int]):
        self.location_type = location_type
        self.included = included
        self.excluded = excluded

    @staticmethod
    def fromDict(user_data: dict) -> "TargetingLocationDTO":
        """
        transform user data into inner object
        :param user_data: dict
        :return:
        """
        return TargetingLocationDTO(location_type=LocationTypeEnum.set(user_data.get("location_type")),
                                    included=user_data.get("included"),
                                    excluded=user_data.get("excluded"))
