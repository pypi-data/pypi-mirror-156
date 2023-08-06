import json
import os

from ts_t1_validator.models.enums.location_type import LocationTypeEnum
from ts_t1_validator.validators.exceptions import ValidationException
from ts_t1_validator.validators.rules.abstract_rule import ValidationRule


class TargetingLocationInList(ValidationRule):
    REGION_PATH = "targeting_location/fixtures/regions.json"
    DMAX_PATH = "targeting_location/fixtures/dmas.json"

    def __init__(self, value, location_type: LocationTypeEnum):
        self.value = value
        self.location_type = location_type
        self.file_path = self.__setFilePath(self.location_type)

    def __setFilePath(self, location_type: LocationTypeEnum) -> str:
        """
        set file path based on location_type
        :param location_type:
        :return: str
        """

        dir_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = self.REGION_PATH if location_type is LocationTypeEnum.REGION else self.DMAX_PATH
        return f"{dir_name}/{json_path}"

    def execute(self):
        """
        based on location_type value should be in one of lists
        """
        with open(self.file_path) as json_file:
            id_list = json.load(json_file)
            if self.value not in id_list:
                raise ValidationException(f"T1 IDs - {self.value} does not exist for {self.location_type.value}")
