import json
import os
import requests as r
from loguru import logger

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'conf_authentik.json')

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

def save_config(data, config=CONFIG_FILE):
    """保存配置文件"""
    try:
        with open(config, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"failed to save config file: {e}")

def update_config_by_apps(apps: dict, conf: dict, config=CONFIG_FILE):
    """更新配置文件中的应用信息"""
    saved_keys = ['name', 'slug', 'meta_launch_url', 'open_in_new_tab', 'meta_description', 'group']
    for app in apps:
        data = {k: app.get(k) for k in saved_keys}
        meta_description = app.get('meta_description', '')
        if 'web' in meta_description:
            cat = 'web'
        elif 'service' in meta_description:
            cat = 'service'
        else:
            cat = 'ignore'
        conf['applications'][cat].update({app['slug']: data})
    save_config(conf, config)

def update_config_by_proxy_providers(proxy_providers: dict, conf: dict, config=CONFIG_FILE):
    """更新配置文件中的应用信息"""
    saved_keys = ['pk', 'name', 'mode', 'external_host']
    for proxy_provider in proxy_providers:
        pk = str(proxy_provider.get('pk'))
        data = {k: proxy_provider.get(k) for k in saved_keys}
        conf['proxy_providers'].update({pk: data})
    save_config(conf, config)


def list_applications(host:str, token:str) -> dict:
    # https://api.goauthentik.io/reference/core-applications-list/
    url = host + '/core/applications/'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    payload = {
        'page_size': 100,
    }
    resp = r.request("GET", url, headers=headers, data=payload)
    if resp.status_code != 200:
        raise RuntimeError(f"failed to list apps: {resp.text}")
    respj = resp.json()
    pagination = respj['pagination']
    apps = respj['results']

    # TODO multi pages
    return apps

def get_application(host:str, token:str, slug: str) -> bool:
    # https://api.goauthentik.io/reference/core-applications-list/
    url = host + f'/core/applications/{slug}/'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    payload = {
        'search': slug,
    }
    resp = r.request("GET", url, headers=headers, data=payload)
    if resp.status_code != 200:
        return False
    return True

def create_application(host: str, token: str, name: str, slug: str, **kwargs) -> None:
    # https://api.goauthentik.io/reference/core-applications-create/
    url = host + '/core/applications/'

    payload = json.dumps({
        "name": name,
        "slug": slug,
        **kwargs
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    resp = r.request("POST", url, headers=headers, data=payload)
    if resp.status_code != 201:
        raise RuntimeError(f"failed to create app '{slug}': {resp.text}")
    print(resp.json())
    logger.info(f"application '{slug}' created successfully")


def update_application(host:str, token:str, slug: str, **kwargs) -> None:
    if not get_application(host, token, slug):
        create_application(host=host, token=token, slug=slug, **kwargs)
    else:
        # https://api.goauthentik.io/reference/core-applications-partial-update/
        url = host + f'/core/applications/{slug}/'

        payload = json.dumps({
            **kwargs
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        resp = r.request("PATCH", url, headers=headers, data=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"failed to update app '{slug}': {resp.text}")
        print(resp.json())
        logger.info(f"application '{slug}' updated successfully")

def list_proxy_providers(host:str, token:str) -> dict:
    url = host + '/providers/proxy/'
    headers = {
        'Accept': 'application/json',
        'Authorization': f"Bearer {token}"
    }

    payload = {
        'page_size': 100,
    }

    resp = r.request("GET", url, headers=headers, data=payload)

    if resp.status_code != 200:
        raise RuntimeError(f"failed to list proxy providers: {resp.text}")
    respj = resp.json()
    pagination = respj['pagination']
    proxy_providers = respj['results']

    # TODO multi pages
    return proxy_providers

def update_proxy_provider(host:str, token:str, pk: int, external_host: str, **kwargs) -> None:
    url = host + f"/providers/proxy/{pk}/"

    payload = json.dumps({
        "external_host": external_host,
        **kwargs
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f"Bearer {token}"
    }

    resp = r.request("PATCH", url, headers=headers, data=payload)
    if resp.status_code != 200:
        raise RuntimeError(f"failed to update proxy_provider {kwargs.get('name', pk)}: {resp.text}")

    print(resp.json())
    logger.info(f"proxy_provider {kwargs.get('name', pk)} updated successfully")


if __name__ == "__main__":
    conf = load_config()
    host = conf["authentik_client"]["host"]
    token = conf["authentik_client"]["access_token"]

    # 不需要改provider
    # proxy_providers = list_proxy_providers(host, token)
    # update_config_by_proxy_providers(proxy_providers, conf)

    # PKS_TOBE_UPDATED = [
    #     '5', '7'
    # ]
    # for pk, data in conf['proxy_providers'].items():
    #     if pk in PKS_TOBE_UPDATED or len(PKS_TOBE_UPDATED) == 0:
    #         update_proxy_provider(host, token, **data)

    # apps = list_applications(host=host, token=token)
    # update_config_by_apps(apps, conf)

    SLUGS_TOBE_UPDATED = [
        # 'sunshine-dash-dd',
    ]

    for slug, data in conf['applications']['web'].items():
        if slug in SLUGS_TOBE_UPDATED or len(SLUGS_TOBE_UPDATED) == 0:
            data['meta_description'] = 'web' + data['meta_description'].replace('web', '')
            update_application(host, token, **data)
    # for slug, data in conf['applications']['service'].items():
    #     if slug in SLUGS_TOBE_UPDATED or len(SLUGS_TOBE_UPDATED) == 0:
    #         data['meta_description'] = 'service' + data['meta_description'].replace('service', '')
    #         update_application(host, token, **data)
    # for slug, data in conf['applications']['ignore'].items():
    #     pass