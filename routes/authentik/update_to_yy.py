import json
import os
import requests
from loguru import logger

logger.add('log_update_to_yy.log', rotation='1 day', retention='3 days')

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config(config=CONFIG_FILE):
    """加载配置文件"""
    try:
        with open(config, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"配置文件不存在: {config}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"配置文件格式错误: {e}")
        return None

def call_update_stun_port_yy():
    ddredirect_config = load_config(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ddredirect', 'config.json'))
    for service_name, port in ddredirect_config['stun_ports'].items():
        payload = {
            'service_name': service_name,
            'ip': ddredirect_config['ips']['ipv4'],
            'port': port,
        }
        webhook_update_stun_port_yy(payload)


def call_update_ip_yy():
    ddredirect_config = load_config(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ddredirect', 'config.json'))
    for ip_type, ip in ddredirect_config['ips'].items():
        payload = {
            'ip': ip,
        }
        webhook_update_ip_yy(ip_type, payload)

def webhook_update_stun_port_yy(payload: dict):
    config = load_config(CONFIG_FILE)
    webhook_stun_port_url = config['webhooks']['stun_port_update_url']
    resp = _webhook_update_yy(webhook_stun_port_url, payload, config['auth']['b64'])
    if resp.status_code != 200:
        logger.error(f"Failed to call STUN port update webhook at {webhook_stun_port_url}: {resp.text}")
        return False
    logger.info(f"STUN port update webhook {webhook_stun_port_url} called successfully: {payload}")
    return True

def webhook_update_ip_yy(ip_type, payload: dict):
    config = load_config(CONFIG_FILE)
    webhook_ip_url = config['webhooks']['ip_update_url_template'].format(ip_type=ip_type)
    resp = _webhook_update_yy(webhook_ip_url, payload, config['auth']['b64'])
    if resp.status_code != 200:
        logger.error(f"Failed to call {ip_type} update webhook at {webhook_ip_url}: {resp.text}")
        return False
    logger.info(f"{ip_type} update webhook {webhook_ip_url} called successfully: {payload}")
    return True

def _webhook_update_yy(url, payload: dict, authorization_b64):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Basic {authorization_b64}",
    }
    resp = requests.request('POST', url, headers=headers, data=json.dumps(payload))
    return resp


# if __name__ == '__main__':
#     call_update_stun_port_yy()
#     call_update_ip_yy()