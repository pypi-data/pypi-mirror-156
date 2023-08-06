import socket

from tsdl.common import util
from tsdl.api import mm, pro


class Manual(object):
    """
    帮助手册
    """

    def __init__(self):
        self._app_manual = 'app:manual'

    def protocol(self, name: str, operation: str, security: str = None, **kwargs):
        """
        获取协议的组帧数据
        """
        parse = pro.manual(protocol=name, operation=operation, security=security)
        return util.replace(parse, **kwargs)

    def app(self, key: str, **kwargs):
        """
        获取操作APP的命令数据
        :param key:
        :return:
        """
        command = mm.get(self._app_manual, key)
        return util.replace(command, **kwargs)


manual = Manual()

if __name__ == '__main__':
    METER_COMM = {
        "step_id": "*STEP_ID",
        "todo": {
            "meter:comm": {
                "msg": "#MESSAGE",
                "channel": '#CHANNEL',
                "frame": "#FRAME"
            }
        }
    }

    APP_Show = {
        "step_id": "*STEP_ID",
        "todo": {
            "app:show": {
                "msg": "#MESSAGE"
            }
        }
    }

    BENCH_POWER_OFF = {
        "step_id": "*STEP_ID",
        "todo": {
            "bench:power_off": {
                "msg": "#MESSAGE",
                "Dev_Port": "#DEV_PORT"
            }
        }
    }

    BENCH_POWER_ON = {
        "step_id": "*STEP_ID",
        "todo": {
            "bench:power_on": {
                "msg": "#MESSAGE",
                "Phase": "#PHASE",
                "Rated_Volt": "#RATED_VOLTAGE",
                "Rated_Curr": "#RATED_CURRENT",
                "Rated_Freq": "#RATE_FREQUENT",
                "PhaseSequence": "#PHASE_SEQUENCE",
                "Revers": "#REVERS",
                "Volt_Per": "#VOLTAGE_PERCENT",
                "Curr_Per": "#CURRENT_PERCENT",
                "IABC": "#IABC",
                "CosP": "#COSP",
                "SModel": "#SMODEL",
                "Dev_Port": "#DEV_PORT"
            }
        }
    }

    BENCH_ADJUST = {
        "step_id": "*STEP_ID",
        "todo": {
            "bench:power_adjust": {
                "msg": "#MESSAGE",
                "Phase": "#PHASE",
                "Rated_Volt": "#RATED_VOLTAGE",
                "Rated_Curr": "#RATED_CURRENT",
                "Rated_Freq": "#RATE_FREQUENT",
                "PhaseSequence": "#PHASE_SEQUENCE",
                "Revers": "#REVERS",
                "Volt_Per": "#VOLTAGE_PERCENT",
                "Curr_Per": "#CURRENT_PERCENT",
                "IABC": "#IABC",
                "CosP": "#COSP",
                "SModel": "#SMODEL",
                "Dev_Port": "#DEV_PORT"
            }
        }
    }

    mm.put('app:manual', 'meter:comm', METER_COMM)
    mm.put('app:manual', 'app:show', APP_Show)
    mm.put('app:manual', 'bench:power_on', BENCH_POWER_ON)
    mm.put('app:manual', 'bench:adjust', BENCH_ADJUST)
    mm.put('app:manual', 'bench:power_off', BENCH_POWER_OFF)
