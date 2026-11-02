import os
from lucky_api import LuckyClient
from loguru import logger

from routes.authentik.update_to_local import webhook_update_ip_local, webhook_update_stun_port_local
from routes.authentik.update_to_yy import webhook_update_ip_yy, webhook_update_stun_port_yy

# fetch ddns list from luck api and update local and yy config

logger.add('log_poll_from_lucky.log', rotation='1 day', retention='3 days')
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'conf_lucky.json')
lucky = LuckyClient()
lucky.load_config(CONFIG_FILE)

# poll ddns list and update local and yy config
ddns_list = lucky.get_ddns_list()
for ddns in ddns_list:
    if ddns["TaskType"] == "IPv6":
        ip = ddns["Ipv6Addr"]
        ip_type = "ipv6_ddasus"
    else:
        ip = ddns["Ipv4Addr"]
        ip_type = "ipv4"
    data = {
        'ip': ip,
    }
    webhook_update_ip_local(ip_type, data)
    webhook_update_ip_yy(ip_type, data)
# poll stun rules and update local and yy config
rules = lucky.get_stun_rules()
# {"service_name": "#{ruleName}", "ip": "#{ip}", "port": #{port}}
for rule in rules:
    data = {
        'service_name': rule['Name'],
        'ip': rule['PublicIp'],
        'port': rule['PublicPort'],
    }
    webhook_update_stun_port_local(data)
    webhook_update_stun_port_yy(data)