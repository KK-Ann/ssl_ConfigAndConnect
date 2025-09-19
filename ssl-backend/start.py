import webview
from ClientAPI import ClientAPI
from ServerAPI import ServerAPI
import os
import sys

class Api:
    """
    聚合 API，把 client 和 server 都暴露给前端
    """
    def __init__(self):
        self._window = None  # <- 私有属性，避免被 pywebview 的 introspection 访问
        self.client = ClientAPI()
        self.server = ServerAPI()
    def set_window(self, window):
        """从外部注入 webview window，或在 __main__ 中调用 api.set_window(window)"""
        self._window = window
        self.server.set_window(window)
        self.client.set_window(window)
    def close_window(self):
        try:
            if self._window:
                # 销毁/关闭窗口
                self._window.destroy()
                return "closed"
            return "no window"
        except Exception as e:
            return f"error: {e}"

    def minimize_window(self):
        try:
            if self._window and hasattr(self._window, "minimize"):
                self._window.minimize()
                return "minimized"
            return "not supported"
        except Exception as e:
            return f"error: {e}"

    def expand_window(self, payload=None):
        try:
            if not self._window:
                return "no window"
            # 优先 maximize，如果需要全屏可改用 toggle_fullscreen（视平台实现）
            if hasattr(self._window, "maximize"):
                self._window.maximize()
                return "maximized"
            if hasattr(self._window, "toggle_fullscreen"):
                self._window.toggle_fullscreen()
                return "fullscreen toggled"
            return "not supported"
        except Exception as e:
            return f"error: {e}"
    # ---------- 客户端 ----------
    def client_connect(self, config):
        return self.client.client_connect(config)

    def client_disconnect(self):
        return self.client.client_disconnect()

    def client_send(self, message):
        return self.client.client_send(message)

    # ---------- 服务端 ----------
    # def get_available_options(self):
    def generate_certificate(self,options: dict):
        return self.server.generate_certificate(options)
    def start_server(self, port=8443, cert=None, key=None):
        return self.server.start_server(port, cert, key)

    def stop_server(self):
        return self.server.stop_server()

    def server_send(self, message):
        return self.server.send_message(message)


if hasattr(sys, '_MEIPASS'):
    # 如果是打包后的可执行文件
    # base_path = sys._MEIPASS
    # 定义 Vue 构建后的 HTML 文件路径return os.path.join(sys._MEIPASS, relative_path)
    html_file_path = os.path.join(sys._MEIPASS, "dist/index.html")
else:
    # 如果是开发环境
    base_path = os.path.dirname(os.path.abspath(__file__))
    # 定义 Vue 构建后的 HTML 文件路径
    html_file_path = os.path.join(base_path, "http://localhost:5173")

# 配置 pywebview 关闭提示的中文翻译
chinese = {
    "global.quitConfirmation": "确定关闭?",
}


def create_window():
    api = Api() # 实例化 Api 类
    window = webview.create_window(
        title="ssl连接程序",  # 窗口标题
        #url = "../ssl-ui/dist/index.html",
        url=html_file_path,  # 加载的 URL
        min_size=(1200, 900),  # 最小尺寸
        # on_top=True,  # 是否始终置顶
        # confirm_close=True,  # 是否确认关闭
        # x=100,  # 窗口水平位置
        # y=100,  # 窗口垂直位置
        js_api=api,  # 将上面实例化后的 Api 对象传给前端 js 调用
        frameless=True,  # 是否无边框
        # private_mode=False,  # 是否以隐私模式启动窗口。如果为 True，浏览器将不会保存浏览历史。
    )
    # --划重点--务必记得需要将上面创建的 window 对象再通过函数传给实例化后的 api 对象
    # api.server.set_window(window)
    api.set_window(window)
    webview.start(localization=chinese)


if __name__ == "__main__":
    create_window()