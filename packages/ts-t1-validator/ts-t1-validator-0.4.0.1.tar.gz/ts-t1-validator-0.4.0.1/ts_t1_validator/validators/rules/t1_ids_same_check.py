from typing import Optional

from .abstract_rule import ValidationRule
from ..exceptions import ValidationException
from ...models.enums.location_type import LocationTypeEnum


class T1CheckIds(ValidationRule):
    def __init__(self, include_value_ids: Optional[list], exclude_value_ids: Optional[list], location_type: LocationTypeEnum):

        self.include_value_ids = include_value_ids
        self.exclude_value_ids = exclude_value_ids
        self.location_type = location_type

    def execute(self):
        if self.include_value_ids is None or self.exclude_value_ids is None:
            return

        intersect = set(self.include_value_ids).intersection(self.exclude_value_ids)
        if len(intersect) > 0:
            raise ValidationException(f"Cannot have the same value id in both exclude and include lists in {self.location_type.value}.")
