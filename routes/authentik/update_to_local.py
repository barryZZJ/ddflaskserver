import json
import os
import requests
from loguru import logger

logger.add('log_update_to_local.log', rotation='1 day', retention='3 days')

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

def webhook_update_stun_port_local(payload: dict):
    config = load_config(CONFIG_FILE)
    webhook_stun_port_url_local = config['webhooks']['stun_port_update_url_local']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Basic {config['auth']['b64']}",
    }
    resp = requests.request('POST', webhook_stun_port_url_local, headers=headers, data=json.dumps(payload))
    if resp.status_code != 200:
        logger.error(f"Failed to call STUN port update webhook at {webhook_stun_port_url_local}: {resp.text}")
        return False
    logger.info(f"STUN port update webhook {webhook_stun_port_url_local} called successfully: {payload}")
    return True

def webhook_update_ip_local(ip_type, payload: dict):
    config = load_config(CONFIG_FILE)
    webhook_ip_url = config['webhooks']['ip_update_url_local_template'].format(ip_type=ip_type)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Basic {config['auth']['b64']}",
    }
    resp = requests.request('POST', webhook_ip_url, headers=headers, data=json.dumps(payload))
    if resp.status_code != 200:
        logger.error(f"Failed to call {ip_type} update webhook at {webhook_ip_url}: {resp.text}")
        return False
    logger.info(f"{ip_type} update webhook {webhook_ip_url} called successfully: {payload}")
    return True

