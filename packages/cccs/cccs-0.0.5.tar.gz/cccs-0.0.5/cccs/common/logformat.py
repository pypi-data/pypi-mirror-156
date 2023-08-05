
from cccs.common.loader import APP_NAME

hostname = 'unknownhost'
# noinspection PyBroadException
try:
    from cccs.common.net import get_hostname
    hostname = get_hostname()
except Exception:  # pylint:disable=W0702
    pass

ip = 'x.x.x.x'
# noinspection PyBroadException
try:
    from cccs.common.net import get_hostip
    ip = get_hostip()
except Exception:  # pylint:disable=W0702
    pass

AL_SYSLOG_FORMAT = f'{ip} AL %(levelname)8s %(process)5d %(name)40s | %(message)s'
AL_LOG_FORMAT = f'%(asctime)-16s %(levelname)8s {hostname} %(process)d %(name)40s | %(message)s'
AL_JSON_FORMAT = f'{{' \
    f'"@timestamp": "%(asctime)s", ' \
    f'"event": {{ "module": "{APP_NAME}", "dataset": "%(name)s" }}, ' \
    f'"host": {{ "ip": "{ip}", "hostname": "{hostname}" }}, ' \
    f'"log": {{ "level": "%(levelname)s", "logger": "%(name)s" }}, ' \
    f'"process": {{ "pid": "%(process)d" }}, ' \
    f'"message": %(message)s}}'
