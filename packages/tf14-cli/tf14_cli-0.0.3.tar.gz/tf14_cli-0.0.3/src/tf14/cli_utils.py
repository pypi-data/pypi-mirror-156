#!/bin/python3
import os

from dataclasses import dataclass
from enum import Enum

from .api_methods import logger

class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


# Path Info 
class PATH_UTILS(ExtendedEnum):
    SCRIPT_DIR = "scripts/"
    SCRIPT_INIT = "init.sh"
    SCRIPT_PLAN = "plan.sh"
    SCRIPT_APPLY = "apply.sh"
    SCRIPT_CLEAN = "clean.sh"

@dataclass
class CLI_Utils():
    path:str = os.path.dirname(os.path.realpath(__file__))
    script_path:str = os.path.realpath( os.path.join(path, PATH_UTILS.SCRIPT_DIR.value) )
    
    def init(self) -> None:
        logger.info("Init is running...")
        self.__exe__(script_name=PATH_UTILS.SCRIPT_INIT.value)
                         
    def plan(self) -> None:
        logger.info("Plan is running...")
        self.__exe__(script_name=PATH_UTILS.SCRIPT_PLAN.value)

    def apply(self) -> None:
        logger.info("Apply is running...")
        self.__exe__(script_name=PATH_UTILS.SCRIPT_APPLY.value)

    def clean(self) -> None:
        logger.info("Clean is running...")
        self.__exe__(script_name=PATH_UTILS.SCRIPT_CLEAN.value)

    def edit(self, script_file:str) -> None:
        logger.info("Edit is running...")
        if script_file in PATH_UTILS.list(): 
            self.__exe__(script_name=script_file, cmd="vi")
        else:
            logger.error("Internal Error: Option does not exist")

    def __exe__(self, script_name, cmd="") -> None:
        tmp_path = os.path.realpath( os.path.join(self.script_path, script_name) )

        if os.path.exists(tmp_path):
            os.system(f"{cmd} {tmp_path}") 
        else:
            logger.error("Internal Error: Path does not exist")

