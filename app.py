import sys
from loguru import logger
from flask import Flask

from utils.consts import APP_PORT, APP_HOST

# import logging
#
#
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.DEBUG
# )

app = Flask(__name__, static_folder='static', static_url_path='/')

logger.add('log_ddflaskserver.log', rotation='1 day', retention='3 days')

from routes.root.root import bp_root
from routes.ddredirect.ddredirect import bp_ddredirect
from routes.authentik.authentik import bp_authentik

app.register_blueprint(bp_root)
app.register_blueprint(bp_authentik)
app.register_blueprint(bp_ddredirect)
if __name__ == '__main__':
    # ? 不能是127.0.0.1，否则服务器的端口不开放
    print('Starting wecom_responder...')
    if sys.argv[-1] == '--debug':
        app.run(APP_HOST, port=APP_PORT, debug=True)
    elif sys.argv[-1] == '--ipv6':
        try:
            app.run(host='::', port=APP_PORT, debug=False, use_reloader=False)
        except Exception as e:
            print(f"IPv6 启动失败: {e}")
    else:
        app.run(host='0.0.0.0', port=APP_PORT, debug=False, use_reloader=False)
        # import threading
        # import signal
        # import time

        # def run_ipv4():
        #     app.run(host='0.0.0.0', port=APP_PORT, debug=False, use_reloader=False)

        # def run_ipv6():
        #     try:
        #         app.run(host='::', port=APP_PORT, debug=False, use_reloader=False)
        #     except Exception as e:
        #         print(f"IPv6 启动失败: {e}")

        # threads = []
        # t4 = threading.Thread(target=run_ipv4, daemon=True)
        # threads.append(t4)
        # t4.start()
        # t6 = threading.Thread(target=run_ipv6, daemon=True)
        # threads.append(t6)
        # t6.start()

        # print('Server started on 0.0.0.0:23222 and [::]:23222')

        # # 支持 Ctrl+C 优雅退出
        # try:
        #     while any(t.is_alive() for t in threads):
        #         time.sleep(0.5)
        # except KeyboardInterrupt:
        #     print('收到 Ctrl+C，正在退出...')