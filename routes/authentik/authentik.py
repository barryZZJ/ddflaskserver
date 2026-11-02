import os
import re
from functools import wraps
from threading import Thread

from flask import Blueprint, request, Response
from loguru import logger

from routes.authentik.update_to_local import webhook_update_stun_port_local
from routes.authentik.update_to_yy import webhook_update_stun_port_yy
from utils.authentik_legacy import load_config, update_application, save_config

# Create a Blueprint object for the main section
bp_authentik = Blueprint('authentik', __name__, url_prefix='/authentik')

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')


def require_auth(f):
    """基本认证装饰器 - 仅用于dashboard"""
    @wraps(f)
    def decorated(*args, **kwargs):
        config = load_config(CONFIG_FILE)
        if not config:
            return "Load config file failed", 500

        auth = request.authorization
        if not auth or not (auth.username == config['auth']['username'] and
                           auth.password == config['auth']['password']):
            return Response(
                'Need authentication', 401,
                {'WWW-Authenticate': 'Basic realm="DD Network Access"'}
            )
        return f(*args, **kwargs)
    return decorated


@bp_authentik.route('/webhook/update_app', methods=['GET','POST'])
@require_auth
def webhook_update_authentik_app():
    """Update Authentik app configuration via webhook
    26.9.20: 由于authentik页面的应用不能即时更新，因此不再使用本接口。改用poll_stun_list.py定时轮询，且只更新ddredirect和yy的dashoboard.
    """
    if request.method == 'GET':
        data = request.args
    elif request.method == 'POST':
        data = request.get_json()
    else:
        logger.error("Unsupported HTTP method.")
    print(data)
    if not data or 'port' not in data or 'service_name' not in data or 'ip' not in data:
        logger.error("Invalid STUN port data. Required: service_name, port, ip.")

    config = load_config(CONFIG_FILE)
    mapping = config['stun_slug_map']
    res = mapping.get(data['service_name'])
    if not res:
        logger.error(f"No slug mapping found for service: {data['service_name']}.")
        return {"error": f"No slug mapping found for service: {data['service_name']}."}, 400
    conf_authentik = load_config()
    host = conf_authentik["authentik_client"]["host"]
    token = conf_authentik["authentik_client"]["access_token"]

    if res['type'] == 'web':
        threads = []
        for slug_, data_ in conf_authentik['applications']['web'].items():
            if 'ddasus' not in data_['meta_launch_url']: continue
            new_url = re.sub(r':\d+', f":{data['port']}", data_['meta_launch_url'])
            if new_url == data_['meta_launch_url']: continue
            new_data = {'meta_launch_url': new_url}

            t = Thread(target=update_application, args=(host, token), kwargs={'slug': slug_, **new_data})
            threads.append(t)
            t.start()
            # update_application(host, token, slug=slug_, **new_data)
            conf_authentik['applications']['web'][slug_]['meta_launch_url'] = new_url
            logger.info(f"Authentik app '{slug_}' update thread started via webhook with new port: {data['port']}")
        [t.join() for t in threads]
    elif res['type'] == 'service':
        slug = res['slug']
        for slug_, data_ in conf_authentik['applications']['service'].items():
            if slug_ == slug and 'ddasus' in data_['name']:
                new_name = re.sub(r':\d+', f":{data['port']}", data_['name'])
                if new_name == data_['name']: continue
                new_desc = re.sub(r':\d+', f":{data['port']}", data_['meta_description'])
                new_data = {'name': new_name, 'meta_description': new_desc}
                update_application(host, token, slug=slug_, **new_data)
                conf_authentik['applications']['service'][slug].update(new_data)
                logger.info(f"Authentik app '{slug}' updated via webhook with new port: {data['port']}")
                break
    else:
        logger.error(f"Unsupported application type for service: {data['service_name']}.")
        return {"error": f"Unsupported application type for service: {data['service_name']}."}, 400

    save_config(conf_authentik)

    threads = []
    threads.append(Thread(target=webhook_update_stun_port_yy, args=(data,)))
    threads.append(Thread(target=webhook_update_stun_port_local, args=(data,)))
    [t.start() for t in threads]

    # if webhook_update_stun_port(data):
    #     logger.info(f"{data['service_name']}: Authentik app and STUN port updated successfully.")
    #     return {"message": f"{data['service_name']}: Authentik app and STUN port updated successfully."}, 200

    # logger.info(f"{data['service_name']}: Authentik app updated successfully but failed to call STUN port update webhook.")
    # return {"message": f"{data['service_name']}: Authentik app updated successfully but failed to call STUN port update webhook."}, 200
    logger.info(f"{data['service_name']}: Authentik app updated successfully.")
    return {"message": f"{data['service_name']}: Authentik app updated successfully."}, 200


