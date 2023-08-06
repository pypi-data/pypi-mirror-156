from enum import unique

from ts_t1_validator.models.enums.abstract_enum import AbstractEnum


@unique
class TargetingTypeEnum(AbstractEnum):
    INCLUDE = "include"
    EXCLUDE = "exclude"
    UNDEFINED = None
