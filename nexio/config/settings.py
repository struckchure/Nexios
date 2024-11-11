from enum import Enum
class BaseConfig(Enum):

    debug :bool  = False

    middleware :list = [] 



BaseConfig.debug