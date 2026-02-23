import json
import os

import authentik_client
from authentik_client import PatchedApplicationRequest
from authentik_client.rest import ApiException
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

def set_launch_url(api_client: authentik_client.ApiClient, slug: str, launch_url: str) -> None:
    """
    使用外部传入的 api_client 更新 authentik 应用的 Launch URL（通过 slug 标识）。
    在成功时静默返回；找不到应用或更新失败会抛出异常。
    参数:
      - api_client: 已创建的 authentik_client.ApiClient 实例（由调用方负责创建与关闭）
      - slug: 应用 slug
      - launch_url: 要设置的 launch url
    """
    api = authentik_client.CoreApi(api_client)

    try:
        resp = api.core_applications_list(slug=slug)
    except ApiException as e:
        raise RuntimeError(f"failed to list apps: {e}") from e

    # 支持两种返回格式：带 results 的分页对象或直接列表
    apps = resp.results if hasattr(resp, "results") else resp

    if len(apps) == 0:
        raise ValueError(f"app with slug '{slug}' not found")

    target = apps[0]

    app_id = None
    for attr in ("pk", "id"):
        if hasattr(target, attr):
            app_id = getattr(target, attr)
            break
    if app_id is None and isinstance(target, dict):
        app_id = target.get("pk") or target.get("id")

    if app_id is None:
        raise RuntimeError("cannot determine application id (pk/id) for update")
    app_id = str(app_id)
    print(f"{app_id=}")

    try:
        api.core_applications_partial_update(app_id, PatchedApplicationRequest(meta_launch_url=launch_url))
    except ApiException as e:
        raise RuntimeError(f"failed to update launch url: {e}") from e


if __name__ == "__main__":
    conf = load_config()
    configuration = authentik_client.Configuration(**conf['authentik_client'])
    api_client = authentik_client.ApiClient(configuration)

    for app_slug, data in conf['applications'].items():
        if data['type'] == 'web':
            set_launch_url(api_client, app_slug, data['launch_url'])
        else:
            # change app's name
            pass