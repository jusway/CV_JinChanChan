import ctypes
import sys

class SystemEnv:
    """系统环境配置类"""

    @staticmethod
    def init_dpi_awareness():
        """强制开启 Windows 高 DPI 感知，防止 125%/150% 缩放导致坐标偏移"""
        # 仅在 Windows 下执行
        if sys.platform != 'win32':
            return

        try:
            # 优先尝试: Per-Monitor DPI Aware V2 (Windows 10 1703+)
            # 核心修改在这里：参数改为 2
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
            print("SystemEnv: DPI感知已启用 (Per-Monitor V2 - 强力模式)")
        except Exception:
            try:
                # 备选方案: System DPI Aware (Windows 8.1+)
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
                print("SystemEnv: DPI感知已启用 (System Aware - 兼容模式)")
            except Exception:
                # 最后的倔强: Legacy DPI Aware (Windows Vista/7)
                ctypes.windll.user32.SetProcessDPIAware()
                print("SystemEnv: DPI感知已启用 (Legacy - 旧版模式)")