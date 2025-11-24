# -*- coding: utf-8 -*-
"""
Sora2 视频生成工具
"""

import sys
import os
import json
import requests
import threading
import time
from datetime import datetime

# 应用版本信息
APP_VERSION = "v1.0.1"
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QLineEdit as OriginalLineEdit, QTextEdit as OriginalTextEdit, QPushButton, 
                              QComboBox, QListWidget, QListWidgetItem, QProgressBar,
                              QFileDialog, QMessageBox, QGroupBox, QScrollArea, QCheckBox,
                              QSpinBox, QFormLayout, QSplitter, QFrame, QMenu, QAction)
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot, QMetaObject, Q_ARG, QUrl
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPainter, QBrush, QPen

# 现代UI组件样式类
class ModernUIComponents:
    # 颜色主题
    PRIMARY_COLOR = QColor(63, 81, 181)  # 主色调 - 深靛蓝色
    SECONDARY_COLOR = QColor(103, 58, 183)  # 辅助色 - 紫色
    ACCENT_COLOR = QColor(0, 188, 212)  # 强调色 - 青色
    BACKGROUND_COLOR = QColor(245, 245, 247)  # 背景色 - 浅灰色
    CARD_COLOR = QColor(255, 255, 255)  # 卡片背景色 - 白色
    TEXT_PRIMARY = QColor(33, 33, 33)  # 主要文本色 - 深灰色
    TEXT_SECONDARY = QColor(117, 117, 117)  # 次要文本色 - 灰色
    BORDER_RADIUS = 8  # 圆角半径
    
    # 设置全局样式表
    @classmethod
    def get_stylesheet(cls):
        return f"""
        /* 主窗口背景 */
        QMainWindow, QWidget {{
            background-color: {cls.rgb_to_hex(cls.BACKGROUND_COLOR)};
        }}
        
        /* 按钮样式 */
        QPushButton {{
            background-color: {cls.rgb_to_hex(cls.PRIMARY_COLOR)};
            color: white;
            border: none;
            border-radius: {cls.BORDER_RADIUS}px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background-color: {cls.rgb_to_hex(cls.SECONDARY_COLOR)};
        }}
        
        QPushButton:pressed {{
            background-color: {cls.rgb_to_hex(cls.PRIMARY_COLOR.darker(120))};
        }}
        
        QPushButton:disabled {{
            background-color: #CCCCCC;
            color: #999999;
        }}
        
        /* 输入框样式 */
        QLineEdit, QTextEdit {{
            background-color: {cls.rgb_to_hex(cls.CARD_COLOR)};
            color: {cls.rgb_to_hex(cls.TEXT_PRIMARY)};
            border: 1px solid #DDDDDD;
            border-radius: {cls.BORDER_RADIUS}px;
            padding: 8px 12px;
            font-size: 14px;
        }}
        
        QLineEdit:focus, QTextEdit:focus {{
            border-color: {cls.rgb_to_hex(cls.PRIMARY_COLOR)};
            outline: none;
        }}
        
        /* 分组框样式 */
        QGroupBox {{
            background-color: {cls.rgb_to_hex(cls.CARD_COLOR)};
            border-radius: {cls.BORDER_RADIUS}px;
            border: 1px solid #EEEEEE;
            margin-top: 10px;
            padding: 10px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px 0 5px;
            color: {cls.rgb_to_hex(cls.TEXT_PRIMARY)};
            font-weight: 500;
        }}
        
        /* 下拉框样式 */
        QComboBox {{
            background-color: {cls.rgb_to_hex(cls.CARD_COLOR)};
            color: {cls.rgb_to_hex(cls.TEXT_PRIMARY)};
            border: 1px solid #DDDDDD;
            border-radius: {cls.BORDER_RADIUS}px;
            padding: 6px 30px 6px 12px;
            font-size: 14px;
        }}
        
        QComboBox:hover {{
            border-color: {cls.rgb_to_hex(cls.PRIMARY_COLOR)};
        }}
        
        QComboBox:editable {{
            background-color: {cls.rgb_to_hex(cls.CARD_COLOR)};
        }}
        
        /* 滚动区域样式 */
        QScrollArea {{
            background-color: {cls.rgb_to_hex(cls.BACKGROUND_COLOR)};
            border: none;
        }}
        
        QScrollArea QWidget {{  /* 滚动区域的内容窗口 */
            background-color: {cls.rgb_to_hex(cls.BACKGROUND_COLOR)};
        }}
        
        QScrollBar:vertical {{
            width: 8px;
            background-color: #F0F0F0;
            border-radius: 4px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: #CCCCCC;
            border-radius: 4px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: #BBBBBB;
        }}
        
        /* 进度条样式 */
        QProgressBar {{
            background-color: #F0F0F0;
            border-radius: 4px;
            text-align: center;
            height: 10px;
        }}
        
        QProgressBar::chunk {{
            background-color: {cls.rgb_to_hex(cls.ACCENT_COLOR)};
            border-radius: 4px;
        }}
        
        /* 列表控件样式 */
        QListWidget {{
            background-color: {cls.rgb_to_hex(cls.CARD_COLOR)};
            border: 1px solid #DDDDDD;
            border-radius: {cls.BORDER_RADIUS}px;
            padding: 5px;
        }}
        
        QListWidget::item {{
            padding: 10px;
            border-bottom: 1px solid #F0F0F0;
        }}
        
        QListWidget::item:hover {{
            background-color: #F5F5F5;
        }}
        
        QListWidget::item:selected {{
            background-color: {cls.rgb_to_hex(cls.PRIMARY_COLOR.lighter(130))};
            color: {cls.rgb_to_hex(cls.TEXT_PRIMARY)};
        }}
        
        /* 选项卡样式 */
        QTabWidget::pane {{
            border: 1px solid #DDDDDD;
            background-color: {cls.rgb_to_hex(cls.CARD_COLOR)};
            border-radius: {cls.BORDER_RADIUS}px;
            padding: 10px;
        }}
        
        QTabBar::tab {{
            background-color: #F0F0F0;
            color: {cls.rgb_to_hex(cls.TEXT_SECONDARY)};
            border-radius: {cls.BORDER_RADIUS}px {cls.BORDER_RADIUS}px 0 0;
            padding: 10px 15px;
            margin-right: 2px;
            min-width: 80px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {cls.rgb_to_hex(cls.CARD_COLOR)};
            color: {cls.rgb_to_hex(cls.PRIMARY_COLOR)};
            font-weight: 500;
        }}
        
        QTabBar::tab:hover {{
            background-color: #E0E0E0;
        }}
        
        /* 复选框样式 */
        QCheckBox {{
            color: {cls.rgb_to_hex(cls.TEXT_PRIMARY)};
            font-size: 14px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid #CCCCCC;
        }}
        
        /* 标签样式 - 确保与底部颜色一致 */
        QLabel {{
            background-color: {cls.rgb_to_hex(cls.CARD_COLOR)};
            color: {cls.rgb_to_hex(cls.TEXT_PRIMARY)};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {cls.rgb_to_hex(cls.PRIMARY_COLOR)};
            border-color: {cls.rgb_to_hex(cls.PRIMARY_COLOR)};
        }}
        
        /* 数值输入框样式 */
        QSpinBox {{
            background-color: {cls.rgb_to_hex(cls.CARD_COLOR)};
            color: {cls.rgb_to_hex(cls.TEXT_PRIMARY)};
            border: 1px solid #DDDDDD;
            border-radius: {cls.BORDER_RADIUS}px;
            padding: 6px;
            font-size: 14px;
        }}
        
        QSpinBox:hover {{
            border-color: {cls.rgb_to_hex(cls.PRIMARY_COLOR)};
        }}
        
        /* 分隔线样式 */
        QSplitter::handle {{
            background-color: #DDDDDD;
        }}
        
        QSplitter::handle:hover {{
            background-color: #CCCCCC;
        }}
        
        /* 状态栏样式 */
        QStatusBar {{
            background-color: {cls.rgb_to_hex(cls.CARD_COLOR)};
            color: {cls.rgb_to_hex(cls.TEXT_SECONDARY)};
            border-top: 1px solid #EEEEEE;
        }}
        
        /* 消息框样式 */
        QMessageBox {{  /* 注意：某些消息框样式可能需要在消息框显示时单独设置 */
            background-color: {cls.rgb_to_hex(cls.CARD_COLOR)};
            border-radius: {cls.BORDER_RADIUS}px;
        }}
        """
    
    # 将QColor转换为CSS十六进制颜色值
    @staticmethod
    def rgb_to_hex(color):
        return f"#{color.red():02x}{color.green():02x}{color.blue():02x}"

# 自定义圆角按钮类
class RoundedPushButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
            QPushButton:pressed {
                background-color: #4338ca;
            }
            QPushButton:disabled {
                background-color: #cbd5e1;
                color: #94a3b8;
            }
        """)

# 自定义卡片组件
class CardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            }
        """)

# 自定义输入框类
class ModernLineEdit(OriginalLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #6366f1;
                outline: none;
            }
        """)

# 自定义文本编辑框类
class ModernTextEdit(OriginalTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border-color: #6366f1;
                outline: none;
            }
        """)
import logging
# 用于表格处理的库
import pandas as pd

# 配置日志
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sora_app.log")
logging.basicConfig(
     level=logging.DEBUG,  # 改为DEBUG级别以获取更多日志信息
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ])
# 添加额外的控制台打印以确保我们能看到输出
print("日志配置完成，日志级别: DEBUG")
print(f"日志文件路径: {log_file}")

# 添加全局异常处理器
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # 对于KeyboardInterrupt，静默处理而不是传递给默认处理程序
        # 这可以防止在PyQt应用程序中因为KeyboardInterrupt导致崩溃
        logging.info("接收到KeyboardInterrupt，已安全处理")
               # 添加更详细的调试信息，记录完整堆栈
        import traceback
        traceback_str = ''.join(traceback.format_tb(exc_traceback))
        # 记录到文件的详细信息
        logging.debug(f"KeyboardInterrupt详细堆栈:\n{traceback_str}")
        # 同时打印到控制台以便快速查看
       # 修复f-string中不能包含反斜杠的问题
        newline = '\n'
        print(f"[DEBUG] KeyboardInterrupt捕获于: {traceback_str.split(newline)[-2].strip() if traceback_str else '未知位置'}")
        return
    
    # 构造更详细的错误信息
    error_class = exc_type.__name__
    error_module = exc_type.__module__
    error_message = str(exc_value)
    
    # 记录异常到日志文件，包含更详细的上下文
    logging.critical(
        f"未处理的异常: {error_module}.{error_class}: {error_message}", 
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    
    # 简化的用户友好错误消息
    user_error_msg = f"发生错误:\n\n{error_class}: {error_message}\n\n详细信息已记录到日志文件中。"
    
    # 尝试在GUI中显示错误信息（线程安全方式）
    try:
        # 先检查是否在Qt环境中
        app = QApplication.instance()
        if app:
            # 确保在主线程中执行GUI操作
            if threading.current_thread() == app.thread():
                # 在主线程中直接显示
                QMessageBox.critical(None, "应用程序错误", user_error_msg)
            else:
                # 在非主线程中使用QMetaObject.invokeMethod
                def show_error_dialog():
                    try:
                        QMessageBox.critical(None, "应用程序错误", user_error_msg)
                    except Exception as msg_error:
                        logging.error(f"显示错误对话框失败: {str(msg_error)}")
                
                # 使用QMetaObject.invokeMethod在线程安全的方式下调用
                try:
                    QMetaObject.invokeMethod(
                        app, 
                        show_error_dialog,
                        Qt.QueuedConnection
                    )
                except Exception as invoke_error:
                    logging.error(f"调度错误对话框失败: {str(invoke_error)}")
        else:
            # 非GUI环境，打印错误到控制台
            print(f"[错误] {user_error_msg}")
    except Exception as gui_error:
        # 如果GUI显示失败，仅记录错误
        logging.error(f"处理GUI错误显示时出错: {str(gui_error)}")

sys.excepthook = handle_exception

class SoraVideoGenerator:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        # 图片上传URL（从文档中获取）
        self.upload_url = "https://imageproxy.zhongzhuan.chat/api/upload"

    def create_video(self, prompt, model="sora-2", orientation="portrait", 
                    size="large", duration=15, images=None):
        """创建视频任务"""
        if images is None:
            images = []
        
        logging.info(f"开始创建视频任务，使用base_url: {self.base_url}")
        
        # 确保使用正确的URL格式 - 无论用户输入什么base_url，都提取协议和主机名部分
        import re
        url_pattern = re.compile(r'^(https?://[^/]+)')
        match = url_pattern.match(self.base_url)
        
        if match:
            # 只保留协议和主机名部分，然后构建标准的API路径
            protocol_host = match.group(1)
            url = f"{protocol_host}/v1/video/create"
            logging.info(f"成功提取协议和主机名: {protocol_host}，构建标准API路径: {url}")
        else:
            # 如果无法提取，使用已知的正确格式
            url = "https://api.sora2.email/v1/video/create"  # 硬编码回退URL
            logging.error(f"无法从base_url提取协议和主机名: {self.base_url}，使用回退URL: {url}")

        logging.info(f"最终使用的API URL: {url}")
              
        # 根据模型类型限制最大时长，但尊重用户选择
        if model == "sora-2-pro":
            if size == "large":
                size = "large"  # sora-2-pro的large是1080p
            # sora-2-pro最大支持15秒，如果用户选择的时长超过15秒，则限制为15秒
            if duration > 15:
                logging.info(f"用户选择的时长{duration}秒超过sora-2-pro支持的最大时长，限制为15秒")
                duration = 15
        else:  # sora-2
            if size == "large":
                size = "large"  # sora-2的large可能是720p
            # 注意：API文档中schema描述sora-2只支持10秒，但example中使用了15秒
            # 这里保留用户选择的时长，让API决定是否接受
            logging.info(f"sora-2模型使用用户选择的时长: {duration}秒")
        
        # 确保duration是整数类型
        if isinstance(duration, str):
            try:
                duration = int(duration)
            except ValueError:
                duration = 10  # 默认10秒
                logging.error(f"无效的时长值: {duration}, 使用默认值10秒")
        
        data = {
            "model": model,
            "orientation": orientation,
            "prompt": prompt,
            "size": size,
            "duration": duration,
            "images": images
        }
               
        logging.info(f"创建视频任务: {model}, {orientation}, {size}, {duration}秒")
        try:
            # 优化超时设置，减少单个请求的最大等待时间
            logging.info(f"准备发送请求到API: {url}")
            logging.info(f"请求参数: model={model}, orientation={orientation}, size={size}, duration={duration}秒")
            logging.info(f"请求数据大小: {len(json.dumps(data))} 字节")
            
            # 减少超时时间，提高响应性
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
                      
            # 详细记录响应信息
            logging.info(f"API响应状态码: {response.status_code}")
            
            # 检查响应状态码
            if response.status_code == 404:
                logging.error(f"404错误 - API路径不存在: {url}")
                logging.error(f"404响应内容: {response.text}")
                # 尝试使用另一种可能的API路径格式
                alternative_url = f"{protocol_host}/video/create" if match else "https://api.sora2.email/video/create"
                logging.info(f"尝试使用替代API路径: {alternative_url}")
                response = requests.post(alternative_url, headers=self.headers, json=data, timeout=60)
                logging.info(f"替代路径响应状态码: {response.status_code}")
            
            # 记录响应内容（限制长度避免日志过大）
            response_text = response.text
            if len(response_text) > 1000:
                response_text = response_text[:1000] + "... (截断，总长度: " + str(len(response.text)) + " 字节)"
            logging.info(f"API响应内容: {response_text}")
             
            response.raise_for_status()
            result = response.json()
            logging.info(f"视频任务创建成功，任务ID: {result.get('id')}")
            return result
        except requests.exceptions.RequestException as e:
            error_message = f"API请求失败: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message += f" - 错误详情: {error_data}"
                except:
                      # 记录响应文本但限制长度
                    error_text = e.response.text
                    if len(error_text) > 500:
                        error_text = error_text[:500] + "... (截断)"
                    error_message += f" - 响应内容: {error_text}"
                error_message += f" - 状态码: {e.response.status_code}"
            logging.error(error_message)
            raise
    
    def query_task(self, task_id):
        """查询任务状态"""
         # 根据查询任务.txt文档，使用正确的API路径格式
        base_url = self.base_url.strip()
         
        # 提取协议和主机名部分
        if base_url.startswith("http://") or base_url.startswith("https://"):
            # 分割协议和主机名+路径
            protocol_end = base_url.find("://") + 3
            host_part = base_url[protocol_end:].split('/')[0]
            protocol = base_url[:protocol_end]
        else:
            # 如果没有协议，默认使用https
            protocol = "https://"
            host_part = base_url.split('/')[0]
        
         # 根据API文档，构建正确的查询任务URL
        # 尝试多种可能的路径格式
        url_candidates = [
            f"{protocol}{host_part}/v1/video/query",  # 标准RESTful格式
            f"{protocol}{host_part}/v1videoquery",    # 文档中提到的格式
            f"{protocol}{host_part}/video/query"       # 可能的简化格式
        ]
        
        params = {"id": task_id}
              
        logging.info(f"查询任务状态: {task_id}")
        logging.info(f"可用的URL候选: {url_candidates}")
        
        # 尝试每个URL，直到找到有效的一个
        for url in url_candidates:
            logging.info(f"尝试URL: {url}")
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                
                # 添加详细的响应日志
                logging.info(f"URL {url} 响应状态码: {response.status_code}")
                
                # 对于200响应，处理结果
                if response.status_code == 200:
                    result = response.json()
                    
                    # 添加更详细的日志记录
                    task_status = result.get('status')
                    video_url = result.get('video_url', 'None')
                    thumbnail_url = result.get('thumbnail_url', 'None')
                    
                    # 特殊处理可能的嵌套响应结构
                    if 'detail' in result and isinstance(result['detail'], dict):
                        detail_status = result['detail'].get('status')
                        if detail_status:
                            # 更新任务状态为detail中的status值
                            result['status'] = detail_status
                            task_status = detail_status
                            logging.info(f"发现嵌套状态信息，更新状态为: {detail_status}")
                    
                    # 日志记录
                    logging.info(f"任务状态查询结果 - ID: {task_id}, 状态: {task_status}")
                    if video_url:
                        logging.info(f"视频URL: {video_url[:50]}...")
                    if thumbnail_url:
                        logging.info(f"缩略图URL: {thumbnail_url[:50]}...")
                    
                    # 记录完整响应以供调试
                    logging.debug(f"完整响应数据: {json.dumps(result, ensure_ascii=False)}")
                    return result
                
                # 如果是404，继续尝试下一个URL
                elif response.status_code == 404:
                    logging.warning(f"URL {url} 返回404错误，尝试下一个URL")
                    continue
                
                # 其他错误状态码
                else:
                    logging.error(f"URL {url} 返回错误状态码: {response.status_code}")
                    try:
                        error_content = response.json()
                        logging.error(f"错误详情: {error_content}")
                    except:
                        logging.error(f"响应内容: {response.text[:200]}...")
                    # 继续尝试下一个URL
                    continue
                    
            except requests.exceptions.RequestException as e:
                error_message = f"URL {url} 请求异常: {str(e)}"
                logging.error(error_message)
                # 继续尝试下一个URL
                continue
        
        # 所有URL都失败
        error_message = f"所有查询URL都尝试失败: {url_candidates}"
        logging.error(error_message)
        raise Exception(error_message)
    
    def upload_file(self, file_path):
        """上传文件到图床，返回图片URL"""
        # 使用文档中指定的图片上传URL
        url = "https://imageproxy.zhongzhuan.chat/api/upload"
        
        # 确保文件存在
        if not os.path.exists(file_path):
            error_message = f"文件不存在: {file_path}"
            logging.error(error_message)
            raise FileNotFoundError(error_message)
        
        logging.info(f"准备上传文件: {file_path} 到图床API: {url}")
        
        try:
            with open(file_path, 'rb') as file:
                files = {'file': (os.path.basename(file_path), file)}
                
                logging.debug(f"开始发送POST请求到图床API")
                response = requests.post(url, files=files, timeout=120)
                
                logging.debug(f"图床API响应状态码: {response.status_code}")
                logging.debug(f"图床API响应内容: {response.text}")
                
                response.raise_for_status()
                
                # 解析JSON响应
                result = response.json()
                logging.debug(f"解析后的JSON响应: {result}")
                
                # 检查响应格式是否正确
                if not isinstance(result, dict) or 'url' not in result:
                    error_message = f"无效的响应格式，缺少'url'字段: {result}"
                    logging.error(error_message)
                    raise ValueError(error_message)
                
                image_url = result['url']
                logging.info(f"图片上传成功，获取到URL: {image_url}")
                return image_url
                
        except json.JSONDecodeError:
            error_message = f"无法解析响应为JSON: {response.text}"
            logging.error(error_message)
            raise
        except requests.exceptions.RequestException as e:
            error_message = f"上传文件失败: {e}"
            if hasattr(e, 'response') and e.response is not None:
                error_message += f" - 响应内容: {e.response.text}"
            logging.error(error_message)
            raise
        except Exception as e:
            logging.error(f"上传过程中发生未知错误: {e}")
            raise

class TextToVideoTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_app = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 提示词设置
        prompt_group = QGroupBox("提示词设置")
        prompt_layout = QVBoxLayout()
                
        # 添加导入表格和导出模板按钮，并排显示
        buttons_h_layout = QHBoxLayout()
        
        self.import_table_btn = QPushButton("导入表格")
        self.import_table_btn.clicked.connect(self.import_table)
        buttons_h_layout.addWidget(self.import_table_btn)
        
        self.export_template_btn = QPushButton("导出模板")
        self.export_template_btn.clicked.connect(self.export_template)
        buttons_h_layout.addWidget(self.export_template_btn)
        
        prompt_layout.addLayout(buttons_h_layout)
        
        self.prompt_text = QTextEdit()
        self.prompt_text.setPlaceholderText("请输入视频描述提示词...")
        # 移除最大高度限制，让输入框可以扩展
        prompt_layout.addWidget(self.prompt_text)
        
        prompt_group.setLayout(prompt_layout)
        layout.addWidget(prompt_group)
        
        # 参数设置
        params_group = QGroupBox("生成参数")
        params_layout = QFormLayout()
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["sora-2", "sora-2-pro"])
        params_layout.addRow("模型:", self.model_combo)
        
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["竖屏", "横屏"])
        params_layout.addRow("方向:", self.orientation_combo)
        
        self.size_combo = QComboBox()
        self.size_combo.addItems(["高清1080p", "一般720p"])
        params_layout.addRow("尺寸:", self.size_combo)
        
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["10"])
        params_layout.addRow("时长(秒):", self.duration_combo)
                
        # 连接模型选择变化信号，动态更新时长选项
        self.model_combo.currentIndexChanged.connect(self.update_duration_options)
        # 初始化时设置正确的时长选项
        self.update_duration_options()
        
        self.batch_count = QSpinBox()
        self.batch_count.setRange(1, 10)
        self.batch_count.setValue(1)
        params_layout.addRow("批量数量:", self.batch_count)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # 操作按钮区域
        buttons_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("生成视频")
        self.generate_btn.clicked.connect(self.generate_videos)
        buttons_layout.addWidget(self.generate_btn)
        
        layout.addLayout(buttons_layout)
        
        # 移除了表格导入说明部分
        
        # 进度显示
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)

    def update_duration_options(self):
        """根据所选模型更新可用的时长选项"""
        model = self.model_combo.currentText()
        current_duration = self.duration_combo.currentText()
        
        # 清空当前选项
        self.duration_combo.clear()
        
        # 注意：API文档中schema和example存在矛盾
        # 为两个模型都提供10秒和15秒选项
        self.duration_combo.addItems(["10", "15"])
        
        # 如果之前选择的值在新选项中存在，则恢复选择，否则默认选择第一个
        if current_duration in [self.duration_combo.itemText(i) for i in range(self.duration_combo.count())]:
            self.duration_combo.setCurrentText(current_duration)
        
    def generate_videos(self):
        """批量生成视频"""
        if not self.main_app.api_key:
            QMessageBox.warning(self, "警告", "请先在设置中配置API Key")
            return
        
        prompt = self.prompt_text.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "警告", "请输入提示词")
            return
        
        # 创建任务队列
        batch_count = self.batch_count.value()
        task_queue = []
        for i in range(batch_count):
                        # 将duration转换为整数
            try:
                duration = int(self.duration_combo.currentText())
            except ValueError:
                duration = 10  # 默认10秒
                logging.error(f"无效的时长值: {self.duration_combo.currentText()}, 使用默认值10秒")

             # 映射中文选项到API参数
            orientation_text = self.orientation_combo.currentText()
            orientation = "portrait" if orientation_text == "竖屏" else "landscape"
            
            size_text = self.size_combo.currentText()
            size = "large" if size_text == "高清1080p" else "small"
                       
            task_info = {
                "prompt": prompt,
                "model": self.model_combo.currentText(),
                "orientation": orientation,
                "size": size,
                 "duration": duration,  # 确保是整数类型
                "batch_index": i + 1
            }
            task_queue.append(task_info)
        
        # 开始生成
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, batch_count)
        self.progress_bar.setValue(0)
        
        # 在UI线程中更新状态栏
        if hasattr(self.main_app, 'show_message'):
            try:
                QMetaObject.invokeMethod(
                    self.main_app,
                    "show_message",
                    Qt.QueuedConnection,
                    Q_ARG(str, f"开始处理 {batch_count} 个视频生成任务")
                )
            except Exception as e:
                logging.error(f"无法更新状态栏: {str(e)}")
        
        # 在新线程中生成视频
        thread = threading.Thread(target=self._generate_batch, args=(task_queue,))
        thread.daemon = True
        thread.start()  # 确保线程正确启动
        thread.start()         
    
    def _generate_batch(self, task_queue):
        """执行批量生成任务队列"""
        generator = self.main_app.generator
        if not generator:
            generator = SoraVideoGenerator(self.main_app.api_key, self.main_app.base_url)
            self.main_app.generator = generator
            
        completed = 0
        success_count = 0
        
        try:
            for i, task_info in enumerate(task_queue):
                try:
                    # 显示当前任务信息
                    current_prompt = task_info["prompt"][:30] + "..." if len(task_info["prompt"]) > 30 else task_info["prompt"]
                    status_text = f"正在生成视频 {i+1}/{len(task_queue)}: {current_prompt}"
                    
                    # 在UI线程中更新状态栏
                    if hasattr(self.main_app, 'show_message'):
                        try:
                            QMetaObject.invokeMethod(
                                self.main_app,
                                "show_message",
                                Qt.QueuedConnection,
                                Q_ARG(str, status_text)
                            )
                        except Exception as e:
                            logging.error(f"无法更新状态栏: {str(e)}")
                    
                    # 调用API创建视频
                    result = generator.create_video(
                        prompt=task_info["prompt"],
                        model=task_info["model"],
                        orientation=task_info["orientation"],
                        size=task_info["size"],
                        duration=task_info["duration"]
                    )
                    
                    # 添加到任务管理
                    task_id = result.get('id', '')
                    if task_id:
                        task_data = {
                            'id': task_id,
                            'type': '文生视频',
                            'prompt': task_info["prompt"],
                            'model': task_info["model"],
                            'orientation': task_info["orientation"],
                            'size': task_info["size"],
                            'duration': task_info["duration"],
                            'status': 'pending',
                            'created_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'video_url': None,
                            'error': None
                        }
                        self.main_app.task_manager.add_task(task_data)
                        success_count += 1
                        
                        if hasattr(self.main_app, 'show_message'):
                            try:
                                QMetaObject.invokeMethod(
                                    self.main_app,
                                    "show_message",
                                    Qt.QueuedConnection,
                                    Q_ARG(str, f"任务 {i+1} 创建成功: {task_id[:8]}...")
                                )
                            except Exception as e:
                                logging.error(f"无法更新状态栏: {str(e)}")
                
                except Exception as e:
                    error_msg = str(e)
                    logging.error(f"生成视频失败 (任务 {i+1}/{len(task_queue)}): {error_msg}")
                    
                    # 将失败的任务也添加到任务管理器，标记为失败状态
                    failed_task_data = {
                        'id': f"failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}",
                        'type': '文生视频',
                        'prompt': task_info["prompt"],
                        'model': task_info["model"],
                        'orientation': task_info["orientation"],
                        'size': task_info["size"],
                        'duration': task_info["duration"],
                        'status': 'failed',
                        'created_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'video_url': None,
                        'error': error_msg
                    }
                    self.main_app.task_manager.add_task(failed_task_data)
                    
                    if hasattr(self.main_app, 'show_message'):
                            try:
                                QMetaObject.invokeMethod(
                                    self.main_app,
                                    "show_message",
                                    Qt.QueuedConnection,
                                    Q_ARG(str, f"任务 {i+1} 创建失败: {error_msg[:30]}..."),
                                    Q_ARG(int, 5000)
                                )
                            except Exception as e:
                                logging.error(f"无法更新状态栏: {str(e)}")
                
                # 更新进度
                    completed += 1
                    try:
                        QMetaObject.invokeMethod(
                            self.progress_bar,
                            "setValue",
                            Qt.QueuedConnection,
                            Q_ARG(int, completed)
                        )
                    except Exception as e:
                        logging.error(f"更新进度条失败: {str(e)}")
                
                # 为了避免API请求过于频繁，添加短暂延迟
                time.sleep(1)
        
        except Exception as e:
            logging.error(f"批量生成任务执行过程中出现严重错误: {str(e)}")
            if hasattr(self.main_app, 'show_message'):
                try:
                    QMetaObject.invokeMethod(
                        self.main_app,
                        "show_message",
                        Qt.QueuedConnection,
                        Q_ARG(str, f"执行过程中出错: {str(e)[:30]}..."),
                        Q_ARG(int, 5000)
                    )
                except Exception as msg_error:
                    logging.error(f"无法更新错误消息: {str(msg_error)}")
        
        finally:
            # 无论成功还是失败，都要恢复UI状态
            logging.info(f"批量生成任务完成，成功: {success_count}, 总计: {len(task_queue)}")
            # 使用QMetaObject.invokeMethod在UI线程中安全地更新UI
            try:
                # 使用QMetaObject.invokeMethod调用_update_ui_after_completion方法
                QMetaObject.invokeMethod(
                    self,
                    "_update_ui_after_completion",
                    Qt.QueuedConnection,
                    Q_ARG(int, success_count),
                    Q_ARG(int, len(task_queue))
                )
                logging.info("已请求在UI线程中更新UI状态")
            except Exception as e:
                logging.error(f"请求更新UI失败: {str(e)}")
                # 如果失败，尝试单独启用按钮
                try:
                    QMetaObject.invokeMethod(
                        self.generate_btn,
                        "setEnabled",
                        Qt.QueuedConnection,
                        Q_ARG(bool, True)
                    )
                    QMetaObject.invokeMethod(
                        self.progress_bar,
                        "setVisible",
                        Qt.QueuedConnection,
                        Q_ARG(bool, False)
                    )
                    logging.info("已请求在UI线程中启用按钮作为备用机制")
                except Exception as inner_e:
                    logging.error(f"请求启用按钮失败: {str(inner_e)}")
    
    def _update_ui_after_completion(self, success_count, total_count):
        """完成后更新UI状态"""
        try:
            logging.debug(f"TextToVideoTab: _update_ui_after_completion called with success_count={success_count}, total_count={total_count}")
            
            # 更新按钮状态
            self.generate_btn.setEnabled(True)
            self.import_table_btn.setEnabled(True)
            
            # 更新进度条
            self.progress_bar.setVisible(False)
            
            # 更新状态栏
            if hasattr(self.main_app, 'show_message'):
                if success_count == total_count:
                    self.main_app.show_message(f"全部 {success_count} 个视频生成任务已提交", 3000)
                else:
                    self.main_app.show_message(f"已提交 {success_count}/{total_count} 个视频生成任务，部分任务失败", 5000)
            
            # 显示完成消息
            QMessageBox.information(self, "完成", f"已提交 {success_count} 个视频生成任务")
            
        except Exception as e:
            logging.error(f"更新UI状态时发生错误: {str(e)}")

    def export_template(self):
        """导出表格模板"""
        try:
            # 创建示例数据，将说明放在表头中
            data = {
                '模型（sora2=1，sora2-pro=2）': [1, 2],
                '时长（秒）': [10, 15],
                '方向（竖屏=1，横屏=2）': [1, 2],
                '提示词': ['一只小猫在花园里玩耍', '日落时分的海滩风景']
            }
            
            # 创建DataFrame
            df = pd.DataFrame(data)
            
            # 显示文件保存对话框
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(
                self, 
                "保存表格模板", 
                "", 
                "Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*)",
                options=options
            )
            
            if file_name:
                # 根据文件扩展名保存为相应格式
                if file_name.endswith('.csv'):
                    df.to_csv(file_name, index=False, encoding='utf-8-sig')
                else:
                    # 默认保存为Excel格式
                    if not file_name.endswith('.xlsx'):
                        file_name += '.xlsx'
                    df.to_excel(file_name, index=False)
                
                # 显示成功消息
                QMessageBox.information(self, "成功", f"表格模板已成功导出到:\n{file_name}")
                logging.info(f"表格模板已成功导出到: {file_name}")
        except Exception as e:
            # 显示错误消息
            QMessageBox.critical(self, "错误", f"导出表格模板时出错:\n{str(e)}")
            logging.error(f"导出表格模板时出错: {str(e)}", exc_info=True)

    def import_table(self):
        """导入表格批量生成视频任务"""
        if not self.main_app.api_key:
            QMessageBox.warning(self, "警告", "请先在设置中配置API Key")
            return
        
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择表格文件", 
            "", 
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return  # 用户取消选择
        
        try:
            # 根据文件扩展名读取表格
            if file_path.lower().endswith('.csv'):
                # 尝试不同的编码
                try:
                    df = pd.read_csv(file_path, encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(file_path, encoding='gbk')
            else:
                # Excel文件
                df = pd.read_excel(file_path)
            
            # 验证表格格式
            if len(df.columns) < 4:
                QMessageBox.warning(self, "格式错误", "表格至少需要包含4列数据（模型、时长、方向、提示词）")
                return
            
            # 验证并处理数据
            task_queue = []
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # 模型映射: 1=sora-2, 2=sora-2-pro
                    model_code = int(row.iloc[0])
                    if model_code == 1:
                        model = "sora-2"
                    elif model_code == 2:
                        model = "sora-2-pro"
                    else:
                        errors.append(f"第{index+2}行: 模型代码无效，必须是1或2")
                        continue
                    
                    # 时长验证: 10或15秒
                    duration = int(row.iloc[1])
                    if duration not in [10, 15]:
                        errors.append(f"第{index+2}行: 时长必须是10或15")
                        continue
                    
                    # 方向映射: 1=竖屏, 2=横屏
                    orientation_code = int(row.iloc[2])
                    if orientation_code == 1:
                        orientation = "portrait"
                    elif orientation_code == 2:
                        orientation = "landscape"
                    else:
                        errors.append(f"第{index+2}行: 方向代码无效，必须是1或2")
                        continue
                    
                    # 提示词
                    prompt = str(row.iloc[3]).strip()
                    if not prompt:
                        errors.append(f"第{index+2}行: 提示词不能为空")
                        continue
                    
                    # 添加到任务队列
                    task_info = {
                        "prompt": prompt,
                        "model": model,
                        "orientation": orientation,
                        "size": "large",  # 默认高清尺寸
                        "duration": duration,
                        "batch_index": index + 1
                    }
                    task_queue.append(task_info)
                    
                except ValueError as e:
                    errors.append(f"第{index+2}行: 数值格式错误 - {str(e)}")
                except Exception as e:
                    errors.append(f"第{index+2}行: 处理错误 - {str(e)}")
            
            # 显示验证错误
            if errors:
                error_msg = "数据验证失败，以下行存在问题：\n" + "\n".join(errors[:10])  # 只显示前10个错误
                if len(errors) > 10:
                    error_msg += f"\n...还有{len(errors)-10}个错误"
                QMessageBox.warning(self, "数据验证失败", error_msg)
                return
            
            # 确认生成
            if not task_queue:
                QMessageBox.information(self, "提示", "没有有效的任务可以生成")
                return
            
            reply = QMessageBox.question(
                self, 
                "确认生成", 
                f"将生成{len(task_queue)}个视频任务，是否继续？",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # 开始生成
            self.generate_btn.setEnabled(False)
            self.import_table_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, len(task_queue))
            self.progress_bar.setValue(0)
            
            # 更新状态栏
            if hasattr(self.main_app, 'show_message'):
                self.main_app.show_message(f"开始处理 {len(task_queue)} 个表格导入的视频任务")
            
            # 在新线程中生成视频
            thread = threading.Thread(target=self._table_import_process, args=(task_queue,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logging.error(f"表格导入错误: {str(e)}")
            QMessageBox.critical(self, "导入失败", f"无法导入表格文件: {str(e)}")
            # 确保在异常情况下也重新启用按钮
            if hasattr(self, 'import_table_btn'):
                self.import_table_btn.setEnabled(True)
            if hasattr(self, 'generate_btn'):
                self.generate_btn.setEnabled(True)
            
    def _table_import_process(self, task_queue):
        """处理表格导入的批量视频生成任务"""
        for idx, task in enumerate(task_queue):
            try:
                # 更新进度条
                QMetaObject.invokeMethod(self.progress_bar, "setValue", Qt.QueuedConnection, Q_ARG(int, idx + 1))
                
                # 准备生成视频所需参数
                prompt = task["prompt"]
                model = task["model"]
                duration = task["duration"]
                orientation = task["orientation"]
                size = task["size"]
                
                # 调用API生成视频
                result = self._process_generation(prompt, model, duration, orientation, size)
                
                if result:
                    # 更新状态栏
                    QMetaObject.invokeMethod(
                        self.main_app,
                        "show_message",
                        Qt.QueuedConnection,
                        Q_ARG(str, f"任务 {idx+1}/{len(task_queue)} 完成: {task['prompt'][:30]}...")
                    )
                else:
                    # 更新状态栏显示错误
                    QMetaObject.invokeMethod(
                        self.main_app,
                        "show_message",
                        Qt.QueuedConnection,
                        Q_ARG(str, f"任务 {idx+1}/{len(task_queue)} 失败: {task['prompt'][:30]}...")
                    )
                    
            except Exception as e:
                logging.error(f"处理批量任务 {idx+1} 时出错: {str(e)}", exc_info=True)
                # 更新状态栏显示错误
                QMetaObject.invokeMethod(
                    self.main_app,
                    "show_message",
                    Qt.QueuedConnection,
                    Q_ARG(str, f"任务 {idx+1}/{len(task_queue)} 出错: {str(e)}")
                )
        
        # 所有任务完成后更新UI
        QMetaObject.invokeMethod(self, "_update_ui_after_completion", Qt.QueuedConnection)
        
        if not file_path:
            return  # 用户取消选择
        
        try:
            # 根据文件扩展名读取表格
            if file_path.lower().endswith('.csv'):
                # 尝试不同的编码
                try:
                    df = pd.read_csv(file_path, encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(file_path, encoding='gbk')
            else:
                # Excel文件
                df = pd.read_excel(file_path)
            
            # 验证表格格式
            if len(df.columns) < 4:
                QMessageBox.warning(self, "格式错误", "表格至少需要包含4列数据")
                return
            
            # 验证并处理数据
            task_queue = []
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # 模型映射: 1=sora-2, 2=sora-2-pro
                    model_code = int(row.iloc[0])
                    if model_code == 1:
                        model = "sora-2"
                    elif model_code == 2:
                        model = "sora-2-pro"
                    else:
                        errors.append(f"第{index+2}行: 模型代码无效，必须是1或2")
                        continue
                    
                    # 时长验证: 10或15秒
                    duration = int(row.iloc[1])
                    if duration not in [10, 15]:
                        errors.append(f"第{index+2}行: 时长必须是10或15")
                        continue
                    
                    # 方向映射: 1=竖屏, 2=横屏
                    orientation_code = int(row.iloc[2])
                    if orientation_code == 1:
                        orientation = "portrait"
                    elif orientation_code == 2:
                        orientation = "landscape"
                    else:
                        errors.append(f"第{index+2}行: 方向代码无效，必须是1或2")
                        continue
                    
                    # 提示词
                    prompt = str(row.iloc[3]).strip()
                    if not prompt:
                        errors.append(f"第{index+2}行: 提示词不能为空")
                        continue
                    
                    # 添加到任务队列
                    task_info = {
                        "prompt": prompt,
                        "model": model,
                        "orientation": orientation,
                        "size": "large",  # 默认高清尺寸
                        "duration": duration,
                        "batch_index": index + 1
                    }
                    task_queue.append(task_info)
                    
                except ValueError as e:
                    errors.append(f"第{index+2}行: 数值格式错误 - {str(e)}")
                except Exception as e:
                    errors.append(f"第{index+2}行: 处理错误 - {str(e)}")
            
            # 显示验证错误
            if errors:
                error_msg = "数据验证失败，以下行存在问题：\n" + "\n".join(errors[:10])  # 只显示前10个错误
                if len(errors) > 10:
                    error_msg += f"\n...还有{len(errors)-10}个错误"
                QMessageBox.warning(self, "数据验证失败", error_msg)
                return
            
            # 确认生成
            if not task_queue:
                QMessageBox.information(self, "提示", "没有有效的任务可以生成")
                return
            
            reply = QMessageBox.question(
                self, 
                "确认生成", 
                f"将生成{len(task_queue)}个视频任务，是否继续？",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # 开始生成
            self.generate_btn.setEnabled(False)
            self.import_table_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, len(task_queue))
            self.progress_bar.setValue(0)
            
            # 更新状态栏
            if hasattr(self.main_app, 'show_message'):
                self.main_app.show_message(f"开始处理 {len(task_queue)} 个表格导入的视频任务")
            
            # 在新线程中生成视频
            thread = threading.Thread(target=self._table_import_process, args=(task_queue,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logging.error(f"表格导入错误: {str(e)}")
            QMessageBox.critical(self, "导入失败", f"无法导入表格文件: {str(e)}")
    
    def _table_import_process(self, task_queue):
        """处理表格导入的批量生成任务"""
        generator = self.main_app.generator
        if not generator:
            generator = SoraVideoGenerator(self.main_app.api_key, self.main_app.base_url)
            self.main_app.generator = generator
            
        completed = 0
        success_count = 0
        
        try:
            for i, task_info in enumerate(task_queue):
                try:
                    # 显示当前任务信息
                    current_prompt = task_info["prompt"][:30] + "..." if len(task_info["prompt"]) > 30 else task_info["prompt"]
                    status_text = f"正在生成视频 {i+1}/{len(task_queue)}: {current_prompt}"
                    
                    # 更新状态栏
                    if hasattr(self.main_app, 'show_message'):
                        self.main_app.show_message(status_text)
                    
                    # 调用API创建视频
                    result = generator.create_video(
                        prompt=task_info["prompt"],
                        model=task_info["model"],
                        orientation=task_info["orientation"],
                        size=task_info["size"],
                        duration=task_info["duration"]
                    )
                    
                    # 添加到任务管理
                    task_id = result.get('id', '')
                    if task_id:
                        task_data = {
                            'id': task_id,
                            'type': '文生视频',
                            'prompt': task_info["prompt"],
                            'model': task_info["model"],
                            'orientation': task_info["orientation"],
                            'size': task_info["size"],
                            'duration': task_info["duration"],
                            'status': 'pending',
                            'created_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'video_url': None,
                            'error': None
                        }
                        self.main_app.task_manager.add_task(task_data)
                        success_count += 1
                        
                        if hasattr(self.main_app, 'show_message'):
                            self.main_app.show_message(f"任务 {i+1} 创建成功: {task_id[:8]}...")
                
                except Exception as e:
                    error_msg = str(e)
                    logging.error(f"生成视频失败 (任务 {i+1}/{len(task_queue)}): {error_msg}")
                    
                    # 将失败的任务也添加到任务管理器，标记为失败状态
                    failed_task_data = {
                        'id': f"failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}",
                        'type': '文生视频',
                        'prompt': task_info["prompt"],
                        'model': task_info["model"],
                        'orientation': task_info["orientation"],
                        'size': task_info["size"],
                        'duration': task_info["duration"],
                        'status': 'failed',
                        'created_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'video_url': None,
                        'error': error_msg
                    }
                    self.main_app.task_manager.add_task(failed_task_data)
                    
                    if hasattr(self.main_app, 'show_message'):
                        self.main_app.show_message(f"任务 {i+1} 创建失败: {error_msg[:30]}...", 5000)
                
                # 更新进度
                completed += 1
                QMetaObject.invokeMethod(self.progress_bar, "setValue", Qt.QueuedConnection, Q_ARG(int, completed))
                
                # 为了避免API请求过于频繁，添加短暂延迟
                time.sleep(1)
        
        except Exception as e:
            logging.error(f"表格批量生成任务执行过程中出现严重错误: {str(e)}")
            if hasattr(self.main_app, 'show_message'):
                self.main_app.show_message(f"执行过程中出错: {str(e)[:30]}...", 5000)
        
        finally:
            # 无论成功还是失败，都要恢复UI状态
            logging.info(f"表格批量生成任务完成，成功: {success_count}, 总计: {len(task_queue)}")
            # 直接在主线程上调用UI更新方法
            try:
                QMetaObject.invokeMethod(self, "_update_ui_after_completion", Qt.QueuedConnection, 
                                        Q_ARG(int, success_count), Q_ARG(int, len(task_queue)))
                logging.info("已通过QMetaObject.invokeMethod请求UI更新")
            except Exception as e:
                logging.error(f"QMetaObject.invokeMethod调用失败: {str(e)}")
                # 如果invokeMethod失败，尝试更直接的方式
                try:
                    # 直接在当前线程中启用按钮（作为备用机制）
                    self.generate_btn.setEnabled(True)
                    self.import_table_btn.setEnabled(True)
                    self.progress_bar.setVisible(False)
                    logging.info("已直接启用按钮作为备用机制")
                except Exception as inner_e:
                    logging.error(f"直接启用按钮失败: {str(inner_e)}")


class ImageToVideoTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_app = parent
        self.image_files = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 提示词区域
        prompt_group = QGroupBox("提示词设置")
        prompt_layout = QVBoxLayout()
                
        # 添加导入表格和导出模板按钮，并排显示
        buttons_h_layout = QHBoxLayout()
        
        self.import_table_btn = QPushButton("导入表格")
        self.import_table_btn.clicked.connect(self.import_table)
        buttons_h_layout.addWidget(self.import_table_btn)
        
        self.export_template_btn = QPushButton("导出模板")
        self.export_template_btn.clicked.connect(self.export_template)
        buttons_h_layout.addWidget(self.export_template_btn)
        
        prompt_layout.addLayout(buttons_h_layout)
        
        self.prompt_text = QTextEdit()
        self.prompt_text.setPlaceholderText("请输入基于图片的视频描述提示词...")
        # 移除最大高度限制，让输入框可以扩展
        prompt_layout.addWidget(self.prompt_text)
        
        prompt_group.setLayout(prompt_layout)
        layout.addWidget(prompt_group)
        
        # 参数设置
        params_group = QGroupBox("生成参数")
        params_layout = QFormLayout()
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["sora-2", "sora-2-pro"])
        params_layout.addRow("模型:", self.model_combo)
        
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["竖屏", "横屏"])
        params_layout.addRow("方向:", self.orientation_combo)
        
        self.size_combo = QComboBox()
        self.size_combo.addItems(["高清1080p", "一般720p"])
        params_layout.addRow("尺寸:", self.size_combo)
        
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["10"])
        params_layout.addRow("时长(秒):", self.duration_combo)
                
        # 连接模型选择变化信号，动态更新时长选项
        self.model_combo.currentIndexChanged.connect(self.update_duration_options)
        # 初始化时设置正确的时长选项
        self.update_duration_options()
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
                
        # 图片上传区域 - 改为简洁的输入框+浏览按钮形式
        image_group = QGroupBox("图片上传")
        image_layout = QHBoxLayout()
        
        # 输入框用于显示或手动输入图片路径/URL
        self.image_path_edit = QLineEdit()
        # 设置为可编辑，允许用户手动输入
        self.image_path_edit.setReadOnly(False)
        self.image_path_edit.setPlaceholderText("请输入图片URL或选择本地图片文件...")
        # 添加文本变化事件处理
        self.image_path_edit.textChanged.connect(self._on_image_path_changed)
        image_layout.addWidget(self.image_path_edit, 1)  # 占据更多空间
        
 # 浏览按钮
        self.add_image_btn = QPushButton("浏览")
        self.add_image_btn.clicked.connect(self.add_images)
        image_layout.addWidget(self.add_image_btn)
        
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)
                
        # 进度条 - 新增
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)  # 默认隐藏
        layout.addWidget(self.progress_bar)
        
        # 生成按钮
        self.generate_btn = QPushButton("生成视频")
        self.generate_btn.clicked.connect(self.generate_video)
        layout.addWidget(self.generate_btn)
        
        self.setLayout(layout)

    def update_duration_options(self):
        """根据所选模型更新可用的时长选项"""
        model = self.model_combo.currentText()
        current_duration = self.duration_combo.currentText()
        
        # 清空当前选项
        self.duration_combo.clear()
        
        # 注意：API文档中schema和example存在矛盾
        # 为两个模型都提供10秒和15秒选项
        self.duration_combo.addItems(["10", "15"])
        
        # 如果之前选择的值在新选项中存在，则恢复选择，否则默认选择第一个
        if current_duration in [self.duration_combo.itemText(i) for i in range(self.duration_combo.count())]:
            self.duration_combo.setCurrentText(current_duration)
        
    def _on_image_path_changed(self):
        """处理用户手动输入图片路径或URL的情况"""
        text = self.image_path_edit.text().strip()
        if not text:
            self.image_url = None
            self.image_files = []
            return
        
        # 检查是否是URL
        if text.startswith(('http://', 'https://')):
            logging.info(f"检测到URL输入: {text}")
            self.image_url = text
            # 清空本地文件列表，因为使用的是URL
            self.image_files = []
        else:
            # 可能是本地文件路径
            logging.info(f"检测到可能的本地文件路径: {text}")
            self.image_files = [text] if os.path.exists(text) else []
            self.image_url = None
    
    def add_images(self):
        # 使用getOpenFileName获取单个文件
        file, _ = QFileDialog.getOpenFileName(
            self, "选择图片文件", "", 
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if not file:  # 如果用户取消选择，直接返回
            return

        # 清空并重置image_files列表，只保存当前选择的文件
        self.image_files.clear()
        self.image_files.append(file)
                
        # 确保有generator实例
        generator = self.main_app.generator
        if not generator:
            generator = SoraVideoGenerator(self.main_app.api_key, self.main_app.base_url)
            self.main_app.generator = generator
                
        try:
            # 上传新图片获取URL
            logging.info(f"正在上传图片: {file}")
            image_url = generator.upload_file(file)
            logging.info(f"图片已添加，URL: {image_url}")

            # 更新输入框显示上传后的URL，而不是本地文件路径
            # 临时断开信号连接，避免触发_on_image_path_changed
            self.image_path_edit.textChanged.disconnect(self._on_image_path_changed)
            self.image_path_edit.setText(image_url)
            self.image_path_edit.textChanged.connect(self._on_image_path_changed)
            # 存储URL到self.image_url属性，供_process_generation方法使用
            self.image_url = image_url
                        
        except Exception as e:
            error_msg = f"上传图片失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.warning(self, "上传失败", error_msg)
                        # 上传失败时，显示本地文件路径
            # 临时断开信号连接，避免触发_on_image_path_changed
            self.image_path_edit.textChanged.disconnect(self._on_image_path_changed)
            self.image_path_edit.setText(file)
            self.image_path_edit.textChanged.connect(self._on_image_path_changed)
            # 清除URL属性
            self.image_url = None
    
    def generate_video(self):
        """基于图片生成视频"""
        logging.info("===== 用户点击了生成视频按钮 =====")
        
        try:
            # 检查API Key
            if not self.main_app.api_key:
                logging.warning("API Key未配置")
                QMessageBox.warning(self, "警告", "请先在设置中配置API Key")
                return
            else:
                logging.info("API Key已配置")
            
            # 检查图片 - 支持URL或本地文件
            if not self.image_url and not self.image_files:
                logging.warning("没有添加任何图片或URL")
                QMessageBox.warning(self, "警告", "请添加图片或输入图片URL")
                return
            else:
                if self.image_url:
                    logging.info(f"使用图片URL: {self.image_url}")
                else:
                    logging.info(f"使用本地图片: {len(self.image_files)} 张")
            
            # 检查提示词
            prompt = self.prompt_text.toPlainText().strip()
            if not prompt:
                logging.warning("未输入提示词")
                QMessageBox.warning(self, "警告", "请输入提示词")
                return
            else:
                logging.info(f"提示词: {prompt[:50]}..." if len(prompt) > 50 else f"提示词: {prompt}")
            
            # 创建任务队列
            task_queue = []
            logging.info("开始创建任务队列")
            
            # 处理图片URL的情况（优先使用URL）
            if self.image_url:
                # 将duration转换为整数
                try:
                    duration_text = self.duration_combo.currentText()
                    duration = int(duration_text)
                    logging.info(f"任务 1: 时长设置为 {duration} 秒")
                except ValueError:
                    duration = 10  # 默认10秒
                    logging.error(f"任务 1: 无效的时长值: {duration_text}, 使用默认值10秒")
                
                # 映射中文选项到API参数
                orientation_text = self.orientation_combo.currentText()
                orientation = "portrait" if orientation_text == "竖屏" else "landscape"
                logging.info(f"任务 1: 方向设置为 {orientation_text} ({orientation})")
                
                size_text = self.size_combo.currentText()
                size = "large" if size_text == "高清1080p" else "small"
                logging.info(f"任务 1: 尺寸设置为 {size_text} ({size})")
                
                model = self.model_combo.currentText()
                logging.info(f"任务 1: 模型设置为 {model}")
                
                task_info = {
                    "image_file": self.image_url,  # 直接使用URL
                    "is_url": True,  # 添加标记表示这是URL
                    "prompt": prompt,
                    "model": model,
                    "orientation": orientation,
                    "size": size,
                    "duration": duration  # 确保是整数类型
                }
                task_queue.append(task_info)
                logging.info(f"任务 1 添加到队列: {self.image_url}")
            else:
                # 处理本地图片文件的情况
                for i, image_file in enumerate(self.image_files):
                    # 将duration转换为整数
                    try:
                        duration_text = self.duration_combo.currentText()
                        duration = int(duration_text)
                        logging.info(f"任务 {i+1}: 时长设置为 {duration} 秒")
                    except ValueError:
                        duration = 10  # 默认10秒
                        logging.error(f"任务 {i+1}: 无效的时长值: {duration_text}, 使用默认值10秒")
                    
                    # 映射中文选项到API参数
                    orientation_text = self.orientation_combo.currentText()
                    orientation = "portrait" if orientation_text == "竖屏" else "landscape"
                    logging.info(f"任务 {i+1}: 方向设置为 {orientation_text} ({orientation})")
                    
                    size_text = self.size_combo.currentText()
                    size = "large" if size_text == "高清1080p" else "small"
                    logging.info(f"任务 {i+1}: 尺寸设置为 {size_text} ({size})")
                    
                    model = self.model_combo.currentText()
                    logging.info(f"任务 {i+1}: 模型设置为 {model}")
                    
                    task_info = {
                        "image_file": image_file,
                        "is_url": False,  # 添加标记表示这是本地文件
                        "prompt": prompt,
                        "model": model,
                        "orientation": orientation,
                        "size": size,
                        "duration": duration  # 确保是整数类型
                    }
                    task_queue.append(task_info)
                    logging.info(f"任务 {i+1} 添加到队列: {os.path.basename(image_file)}")
            
            logging.info(f"任务队列创建完成，共 {len(task_queue)} 个任务")
            
            # 开始处理 - 更新UI状态
            self.generate_btn.setEnabled(False)
                        
            # 安全检查并创建progress_bar（如果不存在）
            if not hasattr(self, 'progress_bar'):
                logging.warning("progress_bar属性不存在，动态创建中...")
                self.progress_bar = QProgressBar()
                # 将进度条添加到布局中
                if hasattr(self, 'layout'):
                    self.layout().addWidget(self.progress_bar)
                    logging.info("已将动态创建的进度条添加到布局")
                else:
                    logging.warning("无法获取布局，进度条已创建但未添加到界面")
            
            # 设置进度条属性
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, len(task_queue))
            self.progress_bar.setValue(0)
            logging.info("UI状态已更新: 按钮禁用，进度条显示")
            
            # 更新状态栏
            if hasattr(self.main_app, 'show_message'):
                message = f"开始处理 {len(task_queue)} 个图片转视频任务"
                self.main_app.show_message(message)
                logging.info(f"显示消息: {message}")
            
            # 在新线程中处理
            logging.info("准备创建处理线程")
            thread = threading.Thread(target=self._process_generation, args=(task_queue,))
            thread.daemon = True
            thread.start()
            logging.info(f"处理线程已启动，线程ID: {thread.ident}")
            
        except Exception as e:
            logging.error(f"generate_video方法执行异常: {str(e)}", exc_info=True)
            # 即使出现异常，也要确保UI状态正确
            self.generate_btn.setEnabled(True)
            if hasattr(self.main_app, 'show_message'):
                self.main_app.show_message(f"启动任务时出错: {str(e)[:30]}...", 5000)
    
    def _process_generation(self, task_queue):
        """处理图片转视频任务队列"""
        logging.info("开始处理图片转视频任务队列")
        generator = self.main_app.generator
        if not generator:
            logging.info("创建SoraVideoGenerator实例")
            generator = SoraVideoGenerator(self.main_app.api_key, self.main_app.base_url)
            self.main_app.generator = generator
            
        completed = 0
        success_count = 0
        
        try:
            logging.info(f"任务队列长度: {len(task_queue)}")
            for i, task_info in enumerate(task_queue):
                image_file = task_info["image_file"]
                is_url = task_info.get("is_url", False)  # 获取is_url标志，默认为False
                
                # 根据是否为URL决定如何获取图片名称
                if is_url:
                    # 从URL中提取文件名或使用URL的一部分作为名称
                    if '/' in image_file:
                        image_name = image_file.split('/')[-1]
                    else:
                        image_name = image_file[:30] + "..." if len(image_file) > 30 else image_file
                else:
                    image_name = os.path.basename(image_file)
                                
                logging.info(f"处理任务 {i+1}/{len(task_queue)}: {image_name} (URL: {is_url})")
                
                try:
                    # 更新状态信息
                    status_text = f"正在处理图片 {i+1}/{len(task_queue)}: {image_name}"
                    if hasattr(self.main_app, 'show_message'):
                        self.main_app.show_message(status_text)
                    
                    # 尝试获取已上传的URL
                    image_url = None
                    logging.info(f"尝试获取图片URL: {image_file}, 是否为URL: {is_url}")
                    
                    # 优先检查是否是表格任务，如果是则直接使用任务中的image_url
                    if task_info.get("from_table", False):
                        image_url = task_info.get("image_url", None)
                        logging.info(f"使用表格任务中的图片URL: {image_url}")
                    else:
                        # 对于非表格任务，检查是否已经存储了图片URL
                        if hasattr(self, 'image_url') and self.image_url:
                            image_url = self.image_url
                            logging.info(f"使用已存储的图片URL: {image_url}")
                        else:
                            logging.info("未找到已存储的图片URL")
                                            
                            # 特殊处理: 如果任务标记为URL类型且未找到已存储的URL，则直接使用image_file作为URL
                            if is_url and not image_url:
                                image_url = image_file
                                logging.info(f"直接使用图片URL作为输入: {image_url}")
                    
                    # 如果不是URL且没有已上传的URL，则上传图片
                    if not is_url and not image_url:
                        logging.info(f"开始上传本地图片: {image_file}")
                        try:
                            image_url = generator.upload_file(image_file)
                            logging.info(f"图片上传完成成功上传结果 - URL: {image_url}")
                        except Exception as upload_error:
                            logging.error(f"图片上传过程异常: {str(upload_error)}")
                            raise
                        
                        if not image_url:
                            error_msg = "图片上传失败，未返回URL"
                            logging.error(f"图片上传失败: {image_file} - {error_msg}")
                            raise Exception(error_msg)
                    
                    if not image_url:
                        error_msg = "获取图片URL失败"
                        logging.error(f"获取图片URL失败: {image_file}")
                        raise Exception(error_msg)

                    # 验证URL格式
                    if not image_url.startswith(('http://', 'https://')):
                        error_msg = f"图片URL格式不正确: {image_url}"
                        logging.error(error_msg)
                        raise Exception(error_msg)
                    
                    logging.info(f"图片URL验证通过: {image_url}")
                                        
                    # 创建视频任务
                    logging.info(f"准备创建视频任务，使用图片URL: {image_url}")
                    logging.info(f"任务参数: model={task_info['model']}, orientation={task_info['orientation']}, size={task_info['size']}, duration={task_info['duration']}")
                    
                    try:
                        result = generator.create_video(
                            prompt=task_info["prompt"],
                            model=task_info["model"],
                            orientation=task_info["orientation"],
                            size=task_info["size"],
                            duration=task_info["duration"],
                            images=[image_url]
                        )
                        logging.info(f"视频任务创建请求已发送")
                    except Exception as create_error:
                        logging.error(f"创建视频任务异常: {str(create_error)}")
                        raise
                                        
                    logging.info(f"视频任务创建成功，返回结果: {result}")
                    
                    # 添加到任务管理
                    task_id = result.get('id', '')
                    logging.info(f"从API响应中提取任务ID: {task_id}")
                    
                    if task_id:
                        task_data = {
                            'id': task_id,
                            'type': '图生视频',
                            'prompt': task_info["prompt"],
                            'image': image_name,
                            'image_path': image_file,
                            'image_url': image_url,
                            'model': task_info["model"],
                            'orientation': task_info["orientation"],
                            'size': task_info["size"],
                            'duration': task_info["duration"],
                            'status': 'pending',
                            'created_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'video_url': None,
                            'error': None,
                            'raw_result': result
                        }
                        
                        # 检查任务管理器是否存在
                        if not hasattr(self.main_app, 'task_manager'):
                            logging.error("任务管理器不存在，无法添加任务")
                            raise Exception("任务管理器不存在")
                        
                        try:
                            self.main_app.task_manager.add_task(task_data)
                            logging.info(f"任务成功添加到任务管理器: {task_id}")
                            success_count += 1
                            
                            if hasattr(self.main_app, 'show_message'):
                                self.main_app.show_message(f"任务 {i+1} 创建成功: {task_id[:8]}...")
                        except Exception as add_error:
                            logging.error(f"添加任务到任务管理器时出错: {str(add_error)}")
                            raise
                    else:
                        logging.warning(f"API返回结果中未包含任务ID: {result}")
                        # 即使没有任务ID，也创建一个本地任务
                        local_task_id = f"local_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
                        task_data = {
                            'id': local_task_id,
                            'type': '图生视频',
                            'prompt': task_info["prompt"],
                            'image': image_name,
                            'image_path': image_file,
                            'image_url': image_url,
                            'model': task_info["model"],
                            'orientation': task_info["orientation"],
                            'size': task_info["size"],
                            'duration': task_info["duration"],
                            'status': 'pending',
                            'created_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'video_url': None,
                            'error': "API未返回任务ID",
                            'raw_result': result
                        }
                        try:
                            self.main_app.task_manager.add_task(task_data)
                            logging.info(f"已创建本地任务记录: {local_task_id}")
                            success_count += 1
                        except Exception as local_add_error:
                            logging.error(f"添加本地任务到任务管理器时出错: {str(local_add_error)}")
                    
                except Exception as e:
                    error_msg = str(e)
                    logging.error(f"处理图片 {image_file} 失败: {error_msg}", exc_info=True)
                    
                    # 将失败的任务也添加到任务管理器
                    failed_task_id = f"failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
                    failed_task_data = {
                        'id': failed_task_id,
                        'type': '图生视频',
                        'prompt': task_info["prompt"],
                        'image': image_name,
                        'image_path': image_file,
                        'image_url': image_url if 'image_url' in locals() and image_url else "上传失败",
                        'model': task_info["model"],
                        'orientation': task_info["orientation"],
                        'size': task_info["size"],
                        'duration': task_info["duration"],
                        'status': 'failed',
                        'created_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'video_url': None,
                        'error': error_msg
                    }
                    
                    # 尝试添加失败任务到任务管理器
                    try:
                        if hasattr(self.main_app, 'task_manager'):
                            self.main_app.task_manager.add_task(failed_task_data)
                            logging.info(f"失败任务已添加到任务管理器: {failed_task_id}")
                        else:
                            logging.error("任务管理器不存在，无法添加失败任务")
                    except Exception as failed_task_error:
                        logging.error(f"添加失败任务到任务管理器时出错: {str(failed_task_error)}")

                    # 显示错误消息                    
                    if hasattr(self.main_app, 'show_message'):
                        display_error = error_msg[:30] + "..." if len(error_msg) > 30 else error_msg
                        self.main_app.show_message(f"任务 {i+1} 处理失败: {display_error}", 5000)
                
                # 更新进度
                completed += 1
                QMetaObject.invokeMethod(self.progress_bar, "setValue", Qt.QueuedConnection, Q_ARG(int, completed))
                
                # 为了避免API请求过于频繁，添加短暂延迟
                time.sleep(1)
        
        except Exception as e:
            error_details = str(e)
            logging.error(f"图片转视频任务执行过程中出现严重错误: {error_details}", exc_info=True)
            if hasattr(self.main_app, 'show_message'):
                display_error = error_details[:30] + "..." if len(error_details) > 30 else error_details
                self.main_app.show_message(f"执行过程中出错: {display_error}", 5000)
        
        finally:
            # 无论成功还是失败，都要恢复UI状态
            total_tasks = len(task_queue) if 'task_queue' in locals() else 0
            logging.info(f"图片转视频任务完成，成功: {success_count}, 总计: {total_tasks}")
            
            # 直接在主线程上调用UI更新方法
            try:
                logging.info("尝试通过QMetaObject.invokeMethod更新UI")
                QMetaObject.invokeMethod(self, "_update_ui_after_completion", Qt.QueuedConnection, 
                                        Q_ARG(int, success_count), Q_ARG(int, total_tasks))
                logging.info("已通过QMetaObject.invokeMethod请求UI更新")
            except Exception as e:
                logging.error(f"QMetaObject.invokeMethod调用失败: {str(e)}", exc_info=True)
                # 如果invokeMethod失败，尝试更直接的方式
                try:
                    # 直接在当前线程中启用按钮（作为备用机制）
                    self.generate_btn.setEnabled(True)
                    # 确保同时启用导入表格按钮
                    if hasattr(self, 'import_table_btn'):
                        self.import_table_btn.setEnabled(True)
                    self.progress_bar.setVisible(False)
                    logging.info("已直接启用所有按钮作为备用机制")
                except Exception as inner_e:
                    logging.error(f"直接启用按钮失败: {str(inner_e)}")

    def export_template(self):
        """导出表格模板，包含图片地址列"""
        try:
            # 创建示例数据，将说明放在表头中
            data = {
                '图片地址': ['https://example.com/image1.jpg', 'https://example.com/image2.jpg'],
                '模型（sora2=1，sora2-pro=2）': [1, 2],
                '时长（秒）': [10, 15],
                '方向（竖屏=1，横屏=2）': [1, 2],
                '提示词': ['基于图片的视频描述', '另一个基于图片的视频描述']
            }
            
            # 创建DataFrame
            df = pd.DataFrame(data)
            
            # 显示文件保存对话框
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(
                self, 
                "保存表格模板", 
                "", 
                "Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*)",
                options=options
            )
            
            if file_name:
                # 根据文件扩展名保存为相应格式
                if file_name.endswith('.csv'):
                    df.to_csv(file_name, index=False, encoding='utf-8-sig')
                else:
                    # 默认保存为Excel格式
                    if not file_name.endswith('.xlsx'):
                        file_name += '.xlsx'
                    df.to_excel(file_name, index=False)
                
                # 显示成功消息
                QMessageBox.information(self, "成功", f"表格模板已成功导出到:\n{file_name}")
                logging.info(f"表格模板已成功导出到: {file_name}")
        except Exception as e:
            # 显示错误消息
            QMessageBox.critical(self, "错误", f"导出表格模板时出错:\n{str(e)}")
            logging.error(f"导出表格模板时出错: {str(e)}", exc_info=True)

    def import_table(self):
        """导入表格批量生成图片视频任务"""
        if not self.main_app.api_key:
            QMessageBox.warning(self, "警告", "请先在设置中配置API Key")
            return
        
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择表格文件", 
            "", 
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return  # 用户取消选择
        
        try:
            # 根据文件扩展名读取表格
            if file_path.lower().endswith('.csv'):
                # 尝试不同的编码
                try:
                    df = pd.read_csv(file_path, encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(file_path, encoding='gbk')
            else:
                # Excel文件
                df = pd.read_excel(file_path)
            
            # 验证表格格式
            if len(df.columns) < 5:
                QMessageBox.warning(self, "格式错误", "表格至少需要包含5列数据（图片地址、模型、时长、方向、提示词）")
                return

            # 初始化生成器实例
            generator = self.main_app.generator
            if not generator:
                generator = SoraVideoGenerator(self.main_app.api_key, self.main_app.base_url)
                self.main_app.generator = generator
                        
            # 验证并处理数据
            task_queue = []
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # 检查图片地址是否存在
                    image_path_or_url = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ''
                    if not image_path_or_url:
                        errors.append(f"第{index+2}行: 图片地址不能为空")
                        continue
                    
                    # 判断是URL还是本地文件路径
                    image_url = image_path_or_url
                    if image_path_or_url.startswith(('http://', 'https://')):
                        # 已经是URL，直接使用
                        logging.info(f"第{index+2}行: 检测到图片URL")
                    else:
                        # 假设是本地文件路径，需要上传
                        logging.info(f"第{index+2}行: 检测到本地图片路径，准备上传: {image_path_or_url}")
                        
                        # 检查文件是否存在
                        if not os.path.exists(image_path_or_url):
                            errors.append(f"第{index+2}行: 本地图片文件不存在")
                            continue
                        
                        # 检查文件是否为图片文件
                        file_ext = os.path.splitext(image_path_or_url)[1].lower()
                        if file_ext not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                            errors.append(f"第{index+2}行: 文件不是有效的图片格式")
                            continue
                        
                        # 上传图片获取URL
                        try:
                            image_url = generator.upload_file(image_path_or_url)
                            logging.info(f"第{index+2}行: 图片上传成功，URL: {image_url}")
                        except Exception as upload_error:
                            errors.append(f"第{index+2}行: 图片上传失败 - {str(upload_error)}")
                            continue
                    
                    # 模型映射: 1=sora-2, 2=sora-2-pro
                    model_value = int(row.iloc[1]) if pd.notna(row.iloc[1]) else 1
                    model = "sora-2" if model_value == 1 else "sora-2-pro"
                    
                    # 时长处理
                    duration = int(row.iloc[2]) if pd.notna(row.iloc[2]) else 10
                    
                    # 方向映射: 1=竖屏(portrait), 2=横屏(landscape)
                    orientation_value = int(row.iloc[3]) if pd.notna(row.iloc[3]) else 1
                    orientation = "portrait" if orientation_value == 1 else "landscape"
                    
                    # 提示词
                    prompt = str(row.iloc[4]) if pd.notna(row.iloc[4]) else ""
                    if not prompt:
                        errors.append(f"第{index+2}行: 提示词不能为空")
                        continue
                    
                    # 尺寸映射
                    size = "large"  # 默认高清1080p
                    
                    # 添加到任务队列
                    task_info = {
                        "image_url": image_url,
                        "original_path": image_path_or_url,  # 保存原始路径，方便调试
                        "model": model,
                        "duration": duration,
                        "orientation": orientation,
                        "size": size,
                        "prompt": prompt
                    }
                    task_queue.append(task_info)
                    
                except ValueError as e:
                    errors.append(f"第{index+2}行: 数值格式错误 - {str(e)}")
                except Exception as e:
                    errors.append(f"第{index+2}行: 处理错误 - {str(e)}")
            
            if errors:
                error_msg = "导入过程中发现以下错误:\n" + "\n".join(errors)
                QMessageBox.warning(self, "数据验证错误", error_msg)
                if not task_queue:
                    return
                
                # 如果有部分数据有效，询问用户是否继续
                reply = QMessageBox.question(
                    self, 
                    "继续导入", 
                    f"发现{len(errors)}个错误，{len(task_queue)}个有效任务。是否继续导入有效任务？",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
            
            if not task_queue:
                QMessageBox.information(self, "提示", "没有发现有效的任务数据")
                return
            
            # 确认导入
            reply = QMessageBox.question(
                self, 
                "确认导入", 
                f"即将导入{len(task_queue)}个图片视频生成任务，是否继续？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # 开始生成
            if hasattr(self, 'generate_btn'):
                self.generate_btn.setEnabled(False)
            self.import_table_btn.setEnabled(False)
            
            # 初始化进度条
            if not hasattr(self, 'progress_bar'):
                self.progress_bar = QProgressBar()
                self.layout().addWidget(self.progress_bar)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, len(task_queue))
            self.progress_bar.setValue(0)
            
            # 更新状态栏
            if hasattr(self.main_app, 'show_message'):
                self.main_app.show_message(f"开始处理 {len(task_queue)} 个表格导入的图片视频任务")
            
            # 在新线程中生成视频
            thread = threading.Thread(target=self._table_import_process, args=(task_queue,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logging.error(f"表格导入错误: {str(e)}")
            QMessageBox.critical(self, "导入失败", f"无法导入表格文件: {str(e)}")
    
    def _table_import_process(self, task_queue):
        """处理表格导入的批量任务"""
        # 为_process_generation方法准备任务队列格式
        processed_task_queue = []
        for task in task_queue:
            # 创建符合_process_generation方法预期的任务格式
            processed_task = {
                "prompt": task["prompt"],
                "model": task["model"],
                "duration": task["duration"],
                "orientation": task["orientation"],
                "size": task["size"],
                "image_url": task["image_url"],
                "original_path": task.get("original_path", ""),
                # 添加一个临时的image_file字段，因为_process_generation方法中使用了它
                "image_file": task.get("original_path", task["image_url"]),
                # 添加表格任务标记，确保优先使用表格中的图片URL
                "from_table": True,
                # 对于URL类型的图片，设置is_url标志
                "is_url": task["image_url"].startswith(("http://", "https://"))
            }
            processed_task_queue.append(processed_task)
        
        try:
            # 直接将处理好的任务队列传递给_process_generation方法
            self._process_generation(processed_task_queue)
        except Exception as e:
            logging.error(f"表格导入任务处理过程中出错: {str(e)}", exc_info=True)
            # 更新状态栏显示错误
            QMetaObject.invokeMethod(
                self.main_app,
                "show_message",
                Qt.QueuedConnection,
                Q_ARG(str, f"表格导入任务处理失败: {str(e)}")
            )
        finally:
            # 所有任务完成后更新UI
            QMetaObject.invokeMethod(self, "_update_ui_after_completion", Qt.QueuedConnection, Q_ARG(int, 1), Q_ARG(int, len(task_queue)))
            
    def _update_ui_after_completion(self, success_count, total_count):
        """完成后更新UI状态"""
        logging.debug(f"ImageToVideoTab: _update_ui_after_completion called with success_count={success_count}, total_count={total_count}")
        logging.debug(f"ImageToVideoTab: 按钮当前状态: {self.generate_btn.isEnabled()}")
        self.generate_btn.setEnabled(True)
        self.import_table_btn.setEnabled(True)
        logging.debug(f"ImageToVideoTab: 按钮启用后状态: {self.generate_btn.isEnabled()}")
        self.progress_bar.setVisible(False)
        
        # 更新状态栏
        if hasattr(self.main_app, 'show_message'):
            if success_count == total_count:
                self.main_app.show_message(f"全部 {success_count} 个图片转视频任务已提交", 3000)
            else:
                self.main_app.show_message(f"已提交 {success_count}/{total_count} 个图片转视频任务，部分任务失败", 5000)
        
        QMessageBox.information(self, "完成", f"已提交 {success_count} 个视频生成任务")

class TaskManagerTab(QWidget):
    task_added = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_app = parent
        self.tasks = []
        self.tasks_file = 'sora_tasks.json'  # 任务保存文件
        self.init_ui()
        self.setup_timer()
        self.load_tasks()  # 加载保存的任务
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 任务列表
        self.task_list = QListWidget()
        self.task_list.itemClicked.connect(self.on_task_selected)
        layout.addWidget(QLabel("任务列表:"))
        layout.addWidget(self.task_list)
        
        # 任务详情
        detail_group = QGroupBox("任务详情")
        detail_layout = QFormLayout()
        
        self.task_id_label = QLabel("")
        self.task_type_label = QLabel("")
        self.task_status_label = QLabel("")
        self.task_prompt_label = QLabel("")
        self.task_time_label = QLabel("")
        
        detail_layout.addRow("任务ID:", self.task_id_label)
        detail_layout.addRow("任务类型:", self.task_type_label)
        detail_layout.addRow("状态:", self.task_status_label)
        detail_layout.addRow("提示词:", self.task_prompt_label)
        detail_layout.addRow("创建时间:", self.task_time_label)
        
        detail_group.setLayout(detail_layout)
        layout.addWidget(detail_group)
                
        # 下载进度条
        self.download_progress_layout = QHBoxLayout()
        self.download_progress_label = QLabel("下载进度:")
        self.download_progress_bar = QProgressBar()
        self.download_progress_bar.setValue(0)
        self.download_progress_bar.setFormat("%p%")  # 显示百分比
        self.download_progress_bar.setVisible(False)  # 初始隐藏
        
        self.download_progress_layout.addWidget(self.download_progress_label)
        self.download_progress_layout.addWidget(self.download_progress_bar)
        layout.addLayout(self.download_progress_layout)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("刷新状态")
        self.refresh_btn.clicked.connect(self.refresh_tasks)
        self.delete_btn = QPushButton("删除任务")
        self.delete_btn.clicked.connect(self.delete_task)
        self.download_btn = QPushButton("下载视频")
        self.download_btn.clicked.connect(self.download_video)
        self.clear_all_btn = QPushButton("清除所有任务")
        self.clear_all_btn.clicked.connect(self.clear_all_tasks)
        
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.download_btn)
        btn_layout.addWidget(self.clear_all_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def setup_timer(self):
        self.timer = QTimer()
        # 连接到新的refresh_all_tasks方法，而不是auto_refresh_tasks
        self.timer.timeout.connect(self.refresh_all_tasks)
        self.timer.start(10000)  # 每10秒自动刷新一次
    
    def add_task(self, task_data):
        self.tasks.append(task_data)
        self.update_task_list()
        self.save_tasks()  # 保存任务
    
    def update_task_list(self):
        self.task_list.clear()
        # 状态中文映射
        status_map = {
            'pending': '等待中',
            'completed': '已完成',
            'failed': '失败',
            'processing': '处理中',
            'queued': '排队中',
            'in_progress': '进行中'
        }
      
        for index, task in enumerate(self.tasks, 1):
            status = task.get('status', 'unknown')
            status_icon = "🟡" if status in ['pending', 'queued'] else "🟢" if status == 'completed' else "🔴"
            status_text = status_map.get(status, status)
            prompt = task.get('prompt', '无提示词')[:20] + '...' if len(task.get('prompt', '')) > 20 else task.get('prompt', '无提示词')
            item_text = f"{index}. {status_icon} {status_text} - {task['type']} - {prompt}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, task)
            self.task_list.addItem(item)
    
    def save_tasks(self):
        """保存任务列表到文件"""
        try:
            # 只保存最近30个任务，避免文件过大
            tasks_to_save = self.tasks[-30:]
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_to_save, f, ensure_ascii=False, indent=2)
            logging.info(f"已保存 {len(tasks_to_save)} 个任务")
        except Exception as e:
            logging.error(f"保存任务失败: {e}")
    
    def load_tasks(self):
        """从文件加载任务列表"""
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
                logging.info(f"已加载 {len(self.tasks)} 个任务")
                self.update_task_list()
        except Exception as e:
            logging.error(f"加载任务失败: {e}")
    
    def on_task_selected(self, item):
        task_data = item.data(Qt.UserRole)
        self.task_id_label.setText(task_data.get('id', ''))
        self.task_type_label.setText(task_data.get('type', ''))
        # 状态中文映射
        status_map = {
            'pending': '等待中',
            'completed': '已完成',
            'failed': '失败',
            'processing': '处理中',
            'queued': '排队中',
            'in_progress': '进行中'
        }
        status = task_data.get('status', '')
        
        # 检查是否为失败状态，如果是则显示失败原因
        if status == 'failed':
            # 尝试从多个位置获取失败原因
            error_message = ''
            
            # 1. 尝试从error_message字段获取（从API响应中提取的）
            if 'error_message' in task_data:
                error_message = task_data['error_message']
            # 2. 尝试从error对象中获取message
            elif 'error' in task_data and isinstance(task_data['error'], dict) and 'message' in task_data['error']:
                error_message = task_data['error']['message']
            # 3. 尝试直接从task_data获取message
            elif 'message' in task_data:
                error_message = task_data['message']
            # 4. 尝试从detail中获取message
            elif 'detail' in task_data and isinstance(task_data['detail'], dict) and 'message' in task_data['detail']:
                error_message = task_data['detail']['message']
            # 5. 从prompt中提取提示词作为参考（如果有）
            elif 'prompt' in task_data:
                # 截取前30个字符作为提示
                error_message = f"提示词: {task_data['prompt'][:30]}..."
            
            # 构建显示文本
            status_text = status_map.get(status, status)
            if error_message:
                status_text += f"：{error_message}"
            self.task_status_label.setText(status_text)
        else:
            # 非失败状态正常显示
            self.task_status_label.setText(status_map.get(status, status))
        self.task_prompt_label.setText(task_data.get('prompt', '')[:50] + '...' if len(task_data.get('prompt', '')) > 50 else task_data.get('prompt', ''))
        self.task_time_label.setText(task_data.get('created_time', ''))
    
    def refresh_tasks(self):
        if not self.main_app.api_key:
            QMessageBox.warning(self, "警告", "请先在设置中配置API Key")
            return
        
       # 显示加载状态
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("刷新中...")
        
        # 保存当前选中的任务
        current_row = self.task_list.currentRow()
        
        thread = threading.Thread(target=self._refresh_tasks_thread, args=(current_row,))
        thread.daemon = True
        thread.start()
    
    def _refresh_tasks_thread(self, current_row):
        try:
            generator = self.main_app.generator
            updated_count = 0
            error_count = 0
            completed_count = 0

            logging.info(f"开始刷新任务线程，总任务数: {len(self.tasks)}")
            
             # 重要：不仅刷新进行中的任务，还刷新所有任务，确保状态同步
            # 即使任务显示为已完成，也重新检查以确保最新状态
            tasks_to_refresh = []
            for task in self.tasks:
                task_status = task.get('status')
                # 刷新所有状态的任务，特别是那些可能已完成但未正确更新的任务
                tasks_to_refresh.append(task)
                logging.info(f"任务 {task.get('id', 'unknown')[:8]}... 状态: {task_status}")
            
            logging.info(f"需要刷新的任务数: {len(tasks_to_refresh)}")
            
            for task in tasks_to_refresh:
                try:
                    task_id = task.get('id', 'unknown')
                    logging.info(f"开始查询任务状态: {task_id[:8]}...")
                    
                    # 调用查询方法
                    result = generator.query_task(task_id)
                                        
                    # 详细记录API响应
                    logging.debug(f"任务 {task_id[:8]}... API响应: {json.dumps(result, ensure_ascii=False)}")
                    
                    # 更新任务状态
                    new_status = result.get('status', task.get('status'))
                    old_status = task.get('status', 'unknown')
                                       
                    # 特殊处理响应中的detail嵌套结构
                    if 'detail' in result and isinstance(result['detail'], dict):
                        detail = result['detail']
                        # 从detail中提取更详细的状态信息
                        if 'status' in detail:
                            detail_status = detail['status']
                            # 如果detail中的状态不同，更新为detail中的状态
                            if detail_status != new_status:
                                logging.info(f"发现detail中状态: {detail_status}，覆盖外层状态: {new_status}")
                                new_status = detail_status
                        
                        # 从detail中提取视频URL（如果有的话）
                        if 'url' in detail and not task.get('video_url'):
                            task['video_url'] = detail['url']
                            logging.info(f"从detail中提取视频URL: {task['video_url'][:50]}...")
                        
                        # 从detail中提取缩略图URL
                        if 'thumbnail_url' in detail and not task.get('thumbnail_url'):
                            task['thumbnail_url'] = detail['thumbnail_url']
                            logging.info(f"从detail中提取缩略图URL: {task['thumbnail_url'][:50]}...")
                        
                         # 已经在上方处理了error和detail中的错误信息，这里不再重复处理
                                                
                    # 确保error字段中的错误信息被正确提取
                    if 'error' in result:
                        error_data = result['error']
                        # 处理error是字典的情况
                        if isinstance(error_data, dict) and 'message' in error_data:
                            task['error_message'] = error_data['message']
                            logging.info(f"从error.message中提取错误信息: {task['error_message']}")
                        # 处理error是字符串的情况
                        elif isinstance(error_data, str):
                            task['error_message'] = error_data
                            logging.info(f"从error字符串中提取错误信息: {task['error_message']}")
                                            # 然后尝试从detail中提取错误信息（作为备用）
                    elif 'detail' in result:
                        detail_data = result['detail']
                        if isinstance(detail_data, dict) and 'message' in detail_data:
                            task['error_message'] = detail_data['message']
                            logging.info(f"从detail.message中提取错误信息: {task['error_message']}")
                        elif isinstance(detail_data, str):
                            task['error_message'] = detail_data
                            logging.info(f"从detail字符串中提取错误信息: {task['error_message']}")
                                      
                    # 更新任务状态                    
                    task['status'] = new_status

                    # 处理完成状态的任务 
                    if new_status == 'completed':
                        # 确保视频URL和缩略图URL被正确设置
                        if result.get('video_url'):
                            task['video_url'] = result['video_url']
                        if result.get('thumbnail_url'):
                            task['thumbnail_url'] = result['thumbnail_url']
                        
                        # 额外检查任务是否真的有视频URL
                        if task.get('video_url'):
                            completed_count += 1
                            logging.info(f"✓ 任务完成: {task_id[:8]}... - 状态从 {old_status} 变为 {new_status}")
                            logging.info(f"✓ 视频URL: {task['video_url'][:50]}...")
                                                        
                            # 如果是新完成的任务（状态从非completed变为completed），触发自动下载
                            if old_status != 'completed':
                                logging.info(f"任务 {task_id[:8]}... 是新完成的任务，准备自动下载")
                                # 使用QMetaObject.invokeMethod在主线程中触发自动下载
                                try:
                                    # 创建自动下载标志
                                    task['auto_downloaded'] = False  # 标记任务尚未自动下载
                                    logging.info(f"已为任务 {task_id[:8]}... 设置自动下载标志")
                                except Exception as auto_dl_error:
                                    logging.error(f"设置自动下载标志失败: {str(auto_dl_error)}")
                        else:
                            logging.warning(f"⚠ 任务显示为completed但没有视频URL: {task_id[:8]}...")
                    elif new_status != old_status:
                        logging.info(f"✓ 任务状态更新: {task_id[:8]}... - {old_status} -> {new_status}")
                    else:
                        logging.info(f"任务状态未变: {task_id[:8]}... - 仍然是 {new_status}")

                    updated_count += 1
                    
                except requests.exceptions.RequestException as e:
                    error_msg = f"网络请求失败: {str(e)}"
                    logging.error(f"查询任务 {task.get('id', 'unknown')[:8]}... 失败: {error_msg}")
                    error_count += 1
                except Exception as e:
                    error_msg = f"未知错误: {str(e)}"
                    logging.error(f"查询任务 {task.get('id')} 失败: {error_msg}", exc_info=True)
                    error_count += 1
                
                # 为了避免API请求过于频繁
                time.sleep(0.5)
        
                logging.info(f"任务刷新完成: 总计 {updated_count} 个任务, 新完成 {completed_count} 个, 失败 {error_count} 个")
            
             # 使用QTimer.singleShot在主线程中安全地更新UI
            # 这是PyQt中推荐的跨线程UI更新方式
            try:
               # 设置标志位
                if not hasattr(self, '_needs_ui_update'):
                    self._needs_ui_update = False
                self._needs_ui_update = True
                
                # 使用QTimer.singleShot确保在主线程中执行UI更新
                # 时间设置为0，表示尽快执行但仍然在主线程事件循环中
                QTimer.singleShot(0, self._update_ui_on_main_thread)
                
                logging.info("任务状态数据已更新，UI更新已通过QTimer调度在主线程执行")
            except Exception as e:
                logging.error(f"调度UI更新时出错: {str(e)}")
             
            # 记录错误消息和总结信息
            if error_count > 0:
                logging.warning(f"部分任务刷新失败 ({error_count}/{len(tasks_to_refresh)})")
              
            logging.info(f"任务状态刷新完成: 更新 {updated_count} 个, 失败 {error_count} 个, 总计 {len(tasks_to_refresh)} 个任务")
            
        except KeyboardInterrupt:
            logging.info("刷新任务线程捕获到KeyboardInterrupt，优雅退出")
        except Exception as e:
            logging.error(f"刷新任务线程发生异常: {str(e)}", exc_info=True)
    
    def _update_ui_on_main_thread(self):
        """在主线程中执行UI更新的辅助方法"""
        try:
            if hasattr(self, '_needs_ui_update') and self._needs_ui_update:
                self.update_ui_after_refresh()
                self._needs_ui_update = False
                logging.info("UI更新已在主线程中完成")
        except Exception as e:
             logging.error(f"在主线程中更新UI时出错: {str(e)}")
 
    def update_ui_after_refresh(self):
        """在主线程中更新UI的槽函数"""
        try:
            logging.info("开始在主线程中更新UI")

            # 检查并处理需要自动下载的任务
            tasks_to_auto_download = []
            if hasattr(self, 'tasks'):
                for task in self.tasks:
                    # 检查任务是否满足自动下载条件
                    if (task.get('status') == 'completed' and 
                        task.get('video_url') and 
                        'auto_downloaded' in task and 
                        not task['auto_downloaded']):
                        tasks_to_auto_download.append(task)
                        # 立即标记为已处理，避免重复下载
                        task['auto_downloaded'] = True
                        logging.info(f"检测到需要自动下载的任务: {task['id'][:8]}...")
                        
            # 保存当前选中的行
            current_row = -1
            if hasattr(self, 'task_list') and self.task_list.count() > 0:
                current_row = self.task_list.currentRow()
                logging.info(f"保存当前选中行: {current_row}")
            
            # 直接更新任务列表
            if hasattr(self, 'update_task_list'):
                self.update_task_list()
                logging.info("已在主线程更新任务列表UI")
            
            # 恢复按钮状态
            if hasattr(self, 'refresh_btn'):
                self.refresh_btn.setEnabled(True)
                self.refresh_btn.setText("刷新状态")
                logging.info("已恢复刷新按钮状态")

             # 恢复选中状态
            if hasattr(self, 'task_list') and self.task_list.count() > 0 and current_row >= 0:
                # 确保索引有效
                if current_row < self.task_list.count():
                    self.task_list.setCurrentRow(current_row)
                    logging.info(f"已恢复选中行: {current_row}")
                else:
                    # 如果之前选中的行不存在，尝试选中第一行
                    self.task_list.setCurrentRow(0)
                    logging.info("已选中第一行作为替代")

            # 执行自动下载
            for task in tasks_to_auto_download:
                logging.info(f"开始自动下载任务: {task['id'][:8]}...")
                self._auto_download_video(task)
                        
            logging.info("UI更新完成")
        except Exception as e:
            logging.error(f"UI更新过程中出错: {str(e)}", exc_info=True)
               
    def refresh_all_tasks(self):
        # 这个新方法替代了auto_refresh_tasks，使用不同的实现方式
        # 目标是刷新所有任务状态，包括已完成但未正确更新的任务
        try:
            if hasattr(self, 'main_app') and self.main_app and hasattr(self, 'tasks') and self.tasks:
                thread = threading.Thread(target=self._safe_refresh)
                thread.daemon = True
                thread.start()
        except:
            pass
    
    # 完全移除auto_refresh_tasks方法，因为setup_timer已直接连接到refresh_all_tasks
    
    def _safe_refresh(self):
        # 实际执行刷新的安全方法
        try:
            logging.info("开始安全刷新任务状态")
            
            if not hasattr(self, 'main_app') or not self.main_app:
                logging.warning("main_app不存在")
                return
            
            if not self.main_app.api_key:
                logging.info("API Key未配置")
                return
            
             # 获取当前选中行
            current_row = -1
            if hasattr(self, 'task_list'):
                current_row = self.task_list.currentRow()
            
             # 调用刷新方法
            self._refresh_tasks_thread(current_row)
            
        except Exception as e:
            logging.error(f"安全刷新过程出错: {str(e)}", exc_info=True)
    
    def delete_task(self):
        current_row = self.task_list.currentRow()
        if current_row >= 0:
            task = self.tasks[current_row]
            task_id = task.get('id', 'unknown')
            task_type = task.get('type', 'unknown')
            
            # 显示确认对话框
            reply = QMessageBox.question(
                self, 
                "确认删除", 
                f"确定要删除任务 {task_id[:8]}... ({task_type}) 吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    self.tasks.pop(current_row)
                    self.update_task_list()
                    logging.info(f"已删除任务: {task_id}")
                    
                    if hasattr(self.main_app, 'show_message'):
                        self.main_app.show_message(f"任务 {task_id[:8]}... 已删除")
                except Exception as e:
                    logging.error(f"删除任务失败: {task_id} - {str(e)}")
                    QMessageBox.critical(self, "错误", f"删除任务失败: {str(e)}")
        else:
            QMessageBox.warning(self, "警告", "请先选择一个任务")
    
    def download_video(self):
        current_row = self.task_list.currentRow()
        if current_row >= 0:
            task = self.tasks[current_row]
            task_id = task.get('id', 'unknown')
            task_status = task.get('status', 'unknown')
            video_url = task.get('video_url', None)
            
            logging.info(f"尝试下载任务视频: {task_id[:8]}..., 状态: {task_status}, 视频URL: {'有' if video_url else '无'}")
            
            # 详细的状态检查，提供更具体的错误信息
            if task_status == 'completed':
                if video_url:
                    logging.info(f"开始下载任务视频: {task_id}")
                    
                    # 选择保存位置，添加序号前缀
                    task_index = current_row + 1  # 任务序号从1开始
                    default_filename = f"{task_index}_sora_video_{task['id'][:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                    save_path, _ = QFileDialog.getSaveFileName(
                        self, "保存视频", 
                        os.path.join(self.main_app.output_dir or os.getcwd(), default_filename),
                        "视频文件 (*.mp4)"
                    )
                    
                    if save_path:
                        # 检查并创建目录（如果不存在）
                        save_dir = os.path.dirname(save_path)
                        try:
                            if not os.path.exists(save_dir):
                                logging.info(f"创建保存目录: {save_dir}")
                                os.makedirs(save_dir, exist_ok=True)
                            
                            if not os.access(save_dir, os.W_OK):
                                QMessageBox.warning(self, "警告", f"无权限写入目录: {save_dir}")
                                logging.error(f"无权限写入目录: {save_dir}")
                                return
                        except Exception as e:
                            QMessageBox.warning(self, "警告", f"无法创建或访问保存目录: {str(e)}")
                            logging.error(f"创建或访问目录失败: {save_dir}, 错误: {e}")
                            return
                        
                        # 显示并重置进度条
                        self.download_progress_bar.setVisible(True)
                        self.download_progress_bar.setValue(0)
                        
                         # 在新线程中下载视频
                        self.download_btn.setEnabled(False)
                        thread = threading.Thread(
                            target=self._download_video_thread, 
                            args=(video_url, save_path, task_id)
                        )
                        thread.daemon = True
                        thread.start()
                else:
                    # 特殊情况：任务状态为completed但没有视频URL
                    QMessageBox.warning(self, "警告", "任务标记为已完成，但系统未返回有效的视频链接。请尝试刷新任务状态后再试。")
                    logging.warning(f"任务状态为completed但无视频URL: {task_id}")
            elif task_status == 'failed':
                error_info = task.get('error', '未知错误')
                QMessageBox.warning(self, "警告", f"任务已失败，无法下载视频\n错误信息: {error_info[:100]}...")
                logging.warning(f"尝试下载失败任务的视频: {task_id} - {error_info}")
            elif task_status in ['pending', 'processing']:
                QMessageBox.warning(self, "警告", "任务尚未完成，请等待任务处理完成后再尝试下载。")
                logging.warning(f"尝试下载未完成任务的视频: {task_id}, 状态: {task_status}")
                error_info = task.get('error', '未知错误')
                # 提供更明确的错误信息
                status_message = "任务状态未知" if task_status == 'unknown' else f"任务状态为 {task_status}"
                url_message = "没有可用的视频链接" if not video_url else "视频链接存在但任务状态不正确"
                QMessageBox.warning(self, "警告", f"无法下载视频。{status_message}。{url_message}。请尝试刷新任务状态后再试。")
                logging.warning(f"无法下载视频: {task_id}, 状态: {task_status}, URL: {'有' if video_url else '无'}")
        else:
            QMessageBox.warning(self, "警告", "请先选择一个任务")
    
    def _download_video_thread(self, video_url, save_path, task_id):
        logging.debug(f"[下载线程开始] 任务ID: {task_id}, 视频URL: {video_url}, 保存路径: {save_path}")
        try:
            logging.info(f"开始下载视频文件: {task_id} -> {os.path.basename(save_path)}")
            logging.debug(f"视频URL分析: {video_url}")
            logging.debug(f"保存路径分析: {save_path}, 目录: {os.path.dirname(save_path)}")
            
            # 安全地显示初始消息
            try:
                logging.debug("检查main_app和show_message方法是否存在")
                if hasattr(self, 'main_app') and hasattr(self.main_app, 'show_message'):
                    logging.debug("调用QMetaObject.invokeMethod显示初始下载消息")
                    QMetaObject.invokeMethod(
                        self.main_app, 
                        "show_message", 
                        Qt.QueuedConnection, 
                        Q_ARG(str, "正在下载视频...")
                    )
                else:
                    logging.warning("main_app或show_message方法不存在")
                logging.debug("初始消息调用成功")
            except Exception as msg_error:
                logging.warning(f"更新状态栏消息失败: {str(msg_error)}")
            
            # 设置更合理的超时和重试
            max_retries = 3
            retry_count = 0
            success = False
            
            logging.debug(f"开始下载循环，最大重试次数: {max_retries}")
            while retry_count < max_retries and not success:
                try:
                    logging.debug(f"下载尝试 {retry_count + 1}/{max_retries}")
                    # 下载视频
                    logging.debug(f"发送GET请求到: {video_url}")
                    response = requests.get(
                        video_url, 
                        stream=True, 
                        timeout=(10, 60),  # 连接超时10秒，读取超时60秒
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                    logging.debug(f"请求响应状态码: {response.status_code}")
                    response.raise_for_status()
                    
                    total_size = int(response.headers.get('content-length', 0))
                    logging.debug(f"获取到文件大小: {total_size} 字节")
                    downloaded_size = 0
                    last_progress_update = 0
                    
                    # 确保目录存在
                    logging.debug(f"准备创建目录: {os.path.dirname(save_path)}")
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    logging.debug(f"目录创建成功或已存在")

                    logging.debug(f"开始写入文件: {save_path}") 
                    with open(save_path, 'wb') as f:
                        for chunk_idx, chunk in enumerate(response.iter_content(chunk_size=8192)):
                            if chunk:
                                f.write(chunk)
                                downloaded_size += len(chunk)
                                
                                # 每5%进度更新一次UI，减少调用频率
                                if total_size > 0:
                                    progress = int(downloaded_size / total_size * 100)
                                    if progress - last_progress_update >= 5 or progress == 100:
                                        last_progress_update = progress
                                        logging.debug(f"进度更新: {progress}%, 已下载: {downloaded_size}/{total_size} 字节")
                                        
                                        # 安全地更新进度条
                                        try:
                                            if hasattr(self, 'download_progress_bar') and self.download_progress_bar is not None:
                                                logging.debug("调用QMetaObject.invokeMethod更新进度条")
                                                QMetaObject.invokeMethod(
                                                    self.download_progress_bar, 
                                                    "setValue", 
                                                    Qt.QueuedConnection, 
                                                    Q_ARG(int, progress)
                                                )
                                                logging.debug("进度条更新调用成功")
                                        except Exception as pb_error:
                                            logging.warning(f"更新进度条失败: {str(pb_error)}")
                                        
                                        # 安全地更新状态栏消息
                                        try:
                                            if hasattr(self, 'main_app') and hasattr(self.main_app, 'show_message'):
                                                logging.debug("调用QMetaObject.invokeMethod更新状态栏消息")
                                                QMetaObject.invokeMethod(
                                                    self.main_app, 
                                                    "show_message", 
                                                    Qt.QueuedConnection, 
                                                    Q_ARG(str, f"正在下载视频... {progress}%")
                                                )
                                                logging.debug("状态栏消息更新调用成功")
                                        except Exception as msg_error:
                                            logging.warning(f"更新状态栏消息失败: {str(msg_error)}")
                                                                       # 每100个chunk记录一次
                            if chunk_idx % 100 == 0:
                                logging.debug(f"下载进度: 已处理 {chunk_idx} 个chunk, 已下载: {downloaded_size} 字节")
                    
                    # 验证文件是否下载完整
                    logging.debug("验证文件下载完整性")
                    file_exists = os.path.exists(save_path)
                    actual_size = os.path.getsize(save_path) if file_exists else 0
                    logging.debug(f"文件存在: {file_exists}, 实际大小: {actual_size} 字节")
                    
                    if file_exists and actual_size >= total_size * 0.99:
                        success = True
                        logging.info(f"文件下载完整，满足验证条件")
                        break
                    else:
                         raise Exception(f"文件下载不完整，预期大小: {total_size}，实际大小: {actual_size}")
                    
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        logging.warning(f"下载超时或连接错误，正在重试 ({retry_count}/{max_retries}): {str(e)}")
                        time.sleep(2)  # 等待2秒后重试
                    else:
                        raise
            
            # 下载完成
            if success:
                final_size = os.path.getsize(save_path)
                logging.info(f"视频下载成功: {save_path} ({final_size} 字节)")
                                
               # 安全地隐藏进度条
                try:
                    if hasattr(self, 'download_progress_bar') and self.download_progress_bar is not None:
                        logging.debug("调用QMetaObject.invokeMethod隐藏进度条")
                        QMetaObject.invokeMethod(
                            self.download_progress_bar, 
                            "setVisible", 
                            Qt.QueuedConnection, 
                            Q_ARG(bool, False)
                        )
                        logging.debug("进度条隐藏调用成功")
                except Exception as pb_error:
                    logging.warning(f"隐藏进度条失败: {str(pb_error)}")
                
                # 显示成功消息
                try:
                    logging.debug("调用QMetaObject.invokeMethod显示成功消息")
                    QMetaObject.invokeMethod(
                        self, 
                        "_show_download_success", 
                        Qt.QueuedConnection,
                        Q_ARG(str, save_path)
                    )
                    logging.debug("成功消息显示调用成功")
                except Exception as show_error:
                    logging.error(f"显示成功消息失败: {str(show_error)}")
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP错误: {str(e)}"
            logging.error(f"下载视频失败 (HTTP错误): {task_id} - {error_msg}")
            try:
                logging.debug("调用QMetaObject.invokeMethod显示HTTP错误消息")
                QMetaObject.invokeMethod(
                    self, 
                    "_show_download_error", 
                    Qt.QueuedConnection,
                    Q_ARG(str, error_msg)
                )
                logging.debug("HTTP错误消息显示调用成功")
            except Exception as show_error:
                logging.error(f"显示错误消息失败: {str(show_error)}")
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求失败: {str(e)}"
            logging.error(f"下载视频失败 (网络错误): {task_id} - {error_msg}")
            try:
                logging.debug("调用QMetaObject.invokeMethod显示网络错误消息")
                QMetaObject.invokeMethod(
                    self, 
                    "_show_download_error", 
                    Qt.QueuedConnection,
                    Q_ARG(str, error_msg)
                )
                logging.debug("网络错误消息显示调用成功")
            except Exception as show_error:
                logging.error(f"显示错误消息失败: {str(show_error)}")
        except Exception as e:
            error_msg = f"下载失败: {str(e)}"
            logging.error(f"下载视频失败 (未知错误): {task_id} - {error_msg}")
            try:
                # 隐藏进度条
                if hasattr(self, 'download_progress_bar') and self.download_progress_bar is not None:
                    logging.debug("调用QMetaObject.invokeMethod隐藏进度条(错误处理)")
                    QMetaObject.invokeMethod(
                        self.download_progress_bar, 
                        "setVisible", 
                        Qt.QueuedConnection,
                        Q_ARG(bool, False)
                    )
                    logging.debug("进度条隐藏调用成功(错误处理)")
                # 显示错误消息
                logging.debug("调用QMetaObject.invokeMethod显示未知错误消息")
                QMetaObject.invokeMethod(
                    self, 
                    "_show_download_error", 
                    Qt.QueuedConnection,
                    Q_ARG(str, error_msg)
                    )
                logging.debug("未知错误消息显示调用成功")
            except Exception as show_error:
                logging.error(f"清理UI和显示错误消息失败: {str(show_error)}")
        finally:
            logging.debug("进入finally块，准备启用下载按钮")
            # 安全地启用下载按钮
            try:
                if hasattr(self, 'download_btn') and self.download_btn is not None:
                    logging.debug("调用QMetaObject.invokeMethod启用下载按钮")
                    QMetaObject.invokeMethod(
                        self.download_btn, 
                        "setEnabled", 
                        Qt.QueuedConnection,
                        Q_ARG(bool, True)
                    )
                    logging.debug("下载按钮启用调用成功")
                else:
                    logging.warning("download_btn不存在")
            except Exception as btn_error:
                logging.warning(f"启用下载按钮失败: {str(btn_error)}")
            logging.debug(f"[下载线程结束] 任务ID: {task_id}, 成功: {success if 'success' in locals() else False}")
    
    def _show_download_success(self, save_path):
        """显示下载成功消息"""
        self.download_btn.setEnabled(True)
        # 隐藏进度条
        self.download_progress_bar.setVisible(False)
        if hasattr(self.main_app, 'show_message'):
            self.main_app.show_message("下载完成")
        QMessageBox.information(self, "成功", f"视频已保存到:\n{save_path}")
    
    def _show_download_error(self, error_msg):
        """显示下载错误消息"""
        self.download_btn.setEnabled(True)
        # 隐藏进度条
        self.download_progress_bar.setVisible(False)
        if hasattr(self.main_app, 'show_message'):
            self.main_app.show_message("下载失败")
        QMessageBox.critical(self, "错误", error_msg)


    def clear_all_tasks(self):
        """清除所有任务"""
        try:
            # 检查是否有任务可清除
            if not hasattr(self, 'tasks') or len(self.tasks) == 0:
                QMessageBox.information(self, "提示", "任务列表已经为空")
                logging.info("尝试清除空任务列表")
                return
            
            # 显示确认对话框
            total_tasks = len(self.tasks)
            reply = QMessageBox.question(
                self, 
                "确认清除", 
                f"确定要清除所有 {total_tasks} 个任务吗？此操作无法撤销。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                logging.info(f"开始清除所有 {total_tasks} 个任务")
                
                # 清空任务列表
                task_ids = [task.get('id', 'unknown')[:8] + '...' for task in self.tasks]
                self.tasks.clear()
                
                # 更新UI
                self.update_task_list()
                
                # 保存清空后的任务列表
                self.save_tasks()
                
                # 清空详情面板
                self.task_id_label.setText("")
                self.task_type_label.setText("")
                self.task_status_label.setText("")
                self.task_prompt_label.setText("")
                self.task_time_label.setText("")
                
                # 隐藏进度条
                self.download_progress_bar.setVisible(False)
                
                logging.info(f"已成功清除所有任务: {', '.join(task_ids)}")
                
                # 显示成功消息
                if hasattr(self.main_app, 'show_message'):
                    self.main_app.show_message("所有任务已清除")
                QMessageBox.information(self, "成功", f"已清除所有 {total_tasks} 个任务")
            else:
                logging.info("用户取消了清除所有任务的操作")
        
        except Exception as e:
            logging.error(f"清除所有任务时出错: {str(e)}")
            QMessageBox.critical(self, "错误", f"清除任务失败: {str(e)}")
        
    def _auto_download_video(self, task):
        """自动下载视频到设置的输出目录"""
        try:
            task_id = task.get('id', 'unknown')
            video_url = task.get('video_url', None)
            task_type = task.get('type', 'video')
            
            logging.info(f"自动下载任务: {task_id[:8]}... - 类型: {task_type}")
            
            if not video_url:
                logging.warning(f"任务 {task_id[:8]}... 没有视频URL，无法自动下载")
                return
            
            # 获取输出目录
            output_dir = os.getcwd()  # 默认使用当前目录
            if hasattr(self, 'main_app') and hasattr(self.main_app, 'output_dir'):
                output_dir = self.main_app.output_dir or output_dir
                logging.info(f"使用设置的输出目录: {output_dir}")
            
            # 生成默认文件名，添加序号前缀
            # 查找任务在列表中的索引（序号从1开始）
            task_index = next((i for i, t in enumerate(self.tasks, 1) if t.get('id') == task_id), 0)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f"{task_index}_sora_{task_type}_{task_id[:8]}_{timestamp}.mp4"
            save_path = os.path.join(output_dir, default_filename)
            
            logging.info(f"自动下载目标路径: {save_path}")
            
            # 检查并创建目录（如果不存在）
            save_dir = os.path.dirname(save_path)
            try:
                if not os.path.exists(save_dir):
                    logging.info(f"创建保存目录: {save_dir}")
                    os.makedirs(save_dir, exist_ok=True)
                
                if not os.access(save_dir, os.W_OK):
                    logging.error(f"无权限写入目录: {save_dir}")
                    return
            except Exception as e:
                logging.error(f"无法创建或访问保存目录: {str(e)}")
                return
            
            # 显示并重置进度条
            self.download_progress_bar.setVisible(True)
            self.download_progress_bar.setValue(0)
            
            # 禁用下载按钮以避免冲突
            self.download_btn.setEnabled(False)
            
            # 在新线程中下载视频
            thread = threading.Thread(
                target=self._download_video_thread, 
                args=(video_url, save_path, task_id)
            )
            thread.daemon = True
            thread.start()
            
            logging.info(f"已启动自动下载线程: {task_id[:8]}...")
            
        except Exception as e:
            logging.error(f"自动下载任务 {task.get('id', 'unknown')[:8]}... 失败: {str(e)}")
            # 确保下载按钮恢复可用
            self.download_btn.setEnabled(True)
            self.download_progress_bar.setVisible(False)

class SettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_app = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # API设置
        api_group = QGroupBox("API设置")
        api_layout = QFormLayout()
        
        self.api_key_edit = QLineEdit()
        # 设置为明文显示，移除密码模式
        # self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setText(self.main_app.api_key or "")
        api_layout.addRow("API Key:", self.api_key_edit)
        
        # 隐藏Base URL和服务器输入框，但保留功能
        self.base_url_edit = QLineEdit()
        self.base_url_edit.setText(self.main_app.base_url or "https://api.sora2.email/v1")
        self.base_url_edit.setVisible(False)  # 隐藏输入框
        api_layout.addRow("", self.base_url_edit)  # 删除标签文字
        
        # API服务器选择 - 隐藏但保留功能
        self.server_combo = QComboBox()
        self.server_combo.addItems([
            "https://api.sora2.email/v1"  # 只保留默认选项
        ])
        self.server_combo.setCurrentText("https://api.sora2.email/v1")  # 设置默认值
        self.server_combo.setVisible(False)  # 隐藏下拉框
        self.server_combo.currentTextChanged.connect(self.on_server_changed)
        api_layout.addRow("", self.server_combo)  # 删除标签文字
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # 输出设置
        output_group = QGroupBox("输出设置")
        output_layout = QHBoxLayout()
        
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setText(self.main_app.output_dir or "")
        output_layout.addWidget(self.output_dir_edit)
        
        self.browse_btn = QPushButton("浏览")
        self.browse_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(self.browse_btn)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # 保存按钮
        self.save_btn = QPushButton("保存设置")
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)
          
          # 作者信息
        author_group = QGroupBox("作者信息")
        author_layout = QVBoxLayout()
        
        author_info = QLabel()
        author_info.setTextFormat(Qt.RichText)
        author_info.setText("""
        <p style='font-size:14pt;'>作者：<a href='copy:沐七' style='font-size:14pt;'>沐七</a></p>
        <p style='font-size:14pt;'>微信：<a href='copy:Xseven888' style='font-size:14pt;'>Xseven888</a></p>
        <p style='font-size:14pt;'>API地址：<a href='https://api.sora2.email/register?aff=J0Aw' style='font-size:14pt;'>https://api.sora2.email/register?aff=J0Aw</a></p>
        """)
        author_info.setTextInteractionFlags(Qt.TextBrowserInteraction)
        # 移除setOpenExternalLinks(True)，避免系统处理自定义协议
        author_info.linkActivated.connect(self.on_link_clicked)
        author_layout.addWidget(author_info)
        
        author_group.setLayout(author_layout)
        layout.addWidget(author_group)
        
        # 版本信息
        version_label = QLabel(f"版本：{APP_VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("font-size: 12pt; color: #666666;")
        layout.addWidget(version_label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def on_server_changed(self, text):
        self.base_url_edit.setText(text)
    
    def on_link_clicked(self, link):
        if link.startswith('copy:'):
            # 处理复制到剪贴板的功能
            text_to_copy = link[5:]  # 移除'copy:'前缀
            clipboard = QApplication.clipboard()
            clipboard.setText(text_to_copy)
            QMessageBox.information(self, '复制成功', f'已复制到剪贴板: {text_to_copy}')
        else:
            # 处理正常URL，在默认浏览器中打开
            from PyQt5.QtCore import QUrl
            from PyQt5.QtGui import QDesktopServices
            QDesktopServices.openUrl(QUrl(link))
    

    
    def on_wechat_link_clicked(self, link):
        """处理微信链接点击事件"""
        if link.startswith('copy:'):
            wechat_id = link.split(':')[1]
            clipboard = QApplication.clipboard()
            clipboard.setText(wechat_id)
            QMessageBox.information(self, "复制成功", f"微信ID '{wechat_id}' 已复制到剪贴板")
            # 记录操作
            logging.info(f"复制微信ID: {wechat_id}")
    
    def on_page_loaded(self, success):
        """处理页面加载完成事件"""
        # 隐藏加载进度条
        self.loading_progress.setVisible(False)
        
        if not success:
            # 显示加载失败的友好提示
            error_html = self.get_error_html(self.current_url, "页面加载失败")
            self.web_view.setHtml(error_html)
            
            # 记录错误日志
            logging.error(f"网页加载失败: {self.current_url}")
            
            # 如果是第二个网站加载失败，提供替代方案
            if self.current_url == "https://ok.tpclick.click/":
                QMessageBox.information(self, "替代方案", 
                                       "第二个查询网站暂时无法访问，建议您：\n"
                                       "1. 使用第一个查询网站\n"
                                       "2. 在默认浏览器中打开\n"
                                       "3. 稍后再试")
    
    def update_loading_progress(self, progress):
        """更新加载进度条"""
        self.loading_progress.setValue(progress)
        
    def refresh_current_page(self):
        """刷新当前页面"""
        if hasattr(self, 'current_url') and self.current_url:
            self.load_webpage(self.current_url)
    
    def get_error_html(self, url, error_message):
        """生成友好的错误页面HTML"""
        # 提供替代链接（如果是第二个网站失败）
        alternative_links = ""
        if url == "https://ok.tpclick.click/":
            alternative_links = f"""
            <div style="margin-top: 15px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
                <h3 style="color: #6c757d;">替代查询网站</h3>
                <ul>
                    <li><a href="https://chaxun.wlai.vip/" style="font-size:14pt;">查询网站1 (chaxun.wlai.vip)</a></li>
                </ul>
            </div>
            """
        
        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    color: #333;
                    line-height: 1.6;
                }}
                .error-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #fff;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h2 {{ color: #dc3545; }}
                a {{
                    color: #007bff;
                    text-decoration: none;
                }}
                a:hover {{ text-decoration: underline; }}
                .error-details {{
                    margin-top: 15px;
                    padding: 10px;
                    background-color: #f8d7da;
                    color: #721c24;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <h2>⚠️ 页面加载失败</h2>
                <p>很抱歉，我们无法加载您请求的网页内容。请尝试以下解决方案：</p>
                <ul>
                    <li><a href="{url}" style="font-size:14pt;">在默认浏览器中打开 {url}</a></li>
                    <li>检查您的网络连接是否正常</li>
                    <li>点击页面顶部的刷新按钮重试</li>
                </ul>
                
                <div class="error-details">
                    <strong>错误信息：</strong> {error_message}
                </div>
                
                {alternative_links}
            </div>
        </body>
        </html>
        """
    
    def browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.output_dir_edit.setText(directory)
    

        if url.startswith('copy:'):
            wechat_id = url.replace('copy:', '')
            clipboard = QApplication.clipboard()
            clipboard.setText(wechat_id)
            QMessageBox.information(self, "复制成功", f"微信号 '{wechat_id}' 已复制到剪贴板")
            logging.info(f"微信号 {wechat_id} 被复制到剪贴板")
    
    def save_settings(self):
        self.main_app.api_key = self.api_key_edit.text().strip()
        self.main_app.base_url = self.base_url_edit.text().strip()
        self.main_app.output_dir = self.output_dir_edit.text().strip()
        
        # 更新生成器
        self.main_app.generator = SoraVideoGenerator(self.main_app.api_key, self.main_app.base_url)
        
        # 保存到配置文件
        config = {
            'api_key': self.main_app.api_key,
            'base_url': self.main_app.base_url,
            'output_dir': self.main_app.output_dir
        }
        
        try:
            with open('sora_app_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"保存配置失败: {e}")
              
        # 更新状态栏信息
        self.main_app.update_status_info()  
        QMessageBox.information(self, "成功", "设置已保存")


class WebViewTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_url = "https://chaxun.wlai.vip/"  # 保存当前加载的URL
        self.init_ui()
    
    def init_ui(self):
        # 创建垂直布局
        layout = QVBoxLayout(self)
        
        # 添加标题
        title_label = QLabel("额度查询")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 使用QWebEngineView来显示网页内容，支持JavaScript
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        self.web_view = QWebEngineView()
        # 设置网页加载完成信号处理
        self.web_view.loadFinished.connect(self.on_page_loaded)
        # 设置网页加载进度信号处理
        self.web_view.loadProgress.connect(self.update_loading_progress)
        layout.addWidget(self.web_view)
        
        # 进度条将在按钮布局中添加
        
        # 创建链接切换按钮
        from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QProgressBar
        button_layout = QHBoxLayout()
        
        btn_site1 = QPushButton("查询网站1")
        btn_site1.clicked.connect(lambda: self.load_webpage("https://chaxun.wlai.vip/"))
        button_layout.addWidget(btn_site1)
        
        # 添加刷新按钮
        self.refresh_button = QPushButton("🔄 刷新")
        self.refresh_button.clicked.connect(self.refresh_current_page)
        button_layout.addWidget(self.refresh_button)
        
        # 添加加载状态指示器
        self.loading_progress = QProgressBar()
        self.loading_progress.setMaximumWidth(150)
        self.loading_progress.setRange(0, 100)
        self.loading_progress.setValue(0)
        self.loading_progress.setVisible(False)
        button_layout.addWidget(self.loading_progress)
        
        # 初始加载第一个网页
        self.current_url = "https://chaxun.wlai.vip/"
        
        button_layout.addStretch()
        
        # 将按钮布局添加到主布局
        layout.addLayout(button_layout)
        
        # 最后加载网页，确保所有UI组件都已初始化
        self.load_webpage(self.current_url)
        
        # 添加所有控件到布局
        layout.addWidget(title_label)
        layout.addSpacing(10)
        layout.addLayout(button_layout)
        layout.addWidget(self.web_view, 1)  # 1表示垂直方向拉伸因子
        layout.addSpacing(10)
        
        # 设置布局
        self.setLayout(layout)
    
    def load_webpage(self, url):
        """加载网页内容到QWebEngineView"""
        try:
            # 显示加载进度条
            self.loading_progress.setVisible(True)
            self.loading_progress.setValue(0)
            
            # 保存当前URL
            self.current_url = url
            
            # 直接使用QWebEngineView的load方法加载URL
            self.web_view.load(QUrl(url))
            self.web_view.setFocus()
            
            # 连接加载进度信号
            self.web_view.loadProgress.connect(self.update_loading_progress)
        except Exception as e:
            # 如果加载失败，显示错误信息和备用链接
            self.loading_progress.setVisible(False)
            error_html = self.get_error_html(url, str(e))
            self.web_view.setHtml(error_html)
            
            # 显示加载错误的消息框
            QMessageBox.warning(self, "加载失败", f"无法加载网页 {url}：{str(e)}")
    
    def on_page_loaded(self, success):
        """
        处理页面加载完成事件
        """
        # 隐藏加载进度条
        self.loading_progress.setVisible(False)
        self.loading_progress.setValue(0)
        
        if not success:
            # 显示错误信息
            error_html = self.get_error_html(self.current_url, "页面加载失败")
            self.web_view.setHtml(error_html)
    
    def update_loading_progress(self, progress):
        """
        更新加载进度条
        """
        self.loading_progress.setValue(progress)
    
    def refresh_current_page(self):
        """
        刷新当前页面
        """
        if hasattr(self, 'current_url') and self.current_url:
            self.load_webpage(self.current_url)
    
    def get_error_html(self, url, error_msg):
        """
        生成错误页面HTML
        """
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>加载失败</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
                h1 {{ color: #e74c3c; }}
                .error-message {{ background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin-top: 10px; }}
                ul {{ margin-top: 10px; }}
                li {{ margin-bottom: 5px; }}
                a {{ color: #1e90ff; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>加载失败</h1>
            <p>无法加载网页，请尝试以下方式：</p>
            <ul>
                <li>检查网络连接</li>
                <li>点击"刷新"按钮重试</li>
                <li>在默认浏览器中打开 <a href="{url}" target="_blank">{url}</a></li>
                <li>尝试使用另一个查询网站</li>
            </ul>
            <div class="error-message">
                错误提示：{error_msg}
            </div>
        </body>
        </html>
        '''
    
    def on_wechat_link_clicked(self, link):
        """处理微信链接点击事件"""
        if link.startswith('copy:'):
            wechat_id = link.split(':')[1]
            clipboard = QApplication.clipboard()
            clipboard.setText(wechat_id)
            QMessageBox.information(self, "复制成功", f"微信ID '{wechat_id}' 已复制到剪贴板")
            # 记录操作
            logging.info(f"复制微信ID: {wechat_id}")
    



class SoraVideoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # 应用全局样式表
        app = QApplication.instance()
        app.setStyleSheet(ModernUIComponents.get_stylesheet())
        self.api_key = ""
        self.base_url = "https://api.sora2.email"
        self.output_dir = ""
        self.generator = None
        self.load_config()
        
        # 设置窗口图标
        try:
            # 处理PyInstaller打包后的情况
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
            else:
                icon_path = 'icon.ico'
                
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                logging.info(f"成功设置窗口图标: {icon_path}")
            else:
                logging.warning(f"无法找到图标文件: {icon_path}")
        except Exception as e:
            logging.error(f"设置窗口图标时出错: {e}")
            
        self.init_ui()
        self.setup_status_bar()
        
        # 在后台线程中检查版本更新
        threading.Thread(target=self._check_version_in_background, daemon=True).start()
        
    def _check_version_in_background(self):
        """在后台线程中检查版本更新"""
        logging.info("开始后台版本检查...")
        try:
            # 稍微延迟一下，确保应用已经启动完全
            time.sleep(2)
            logging.info(f"当前应用版本: {APP_VERSION}")
            
            latest_version, release_notes = self.check_latest_version()
            if latest_version:
                logging.info(f"检测到新版本: {latest_version}，准备显示更新通知")
                # 使用QMetaObject.invokeMethod确保在UI线程中显示消息框
                QMetaObject.invokeMethod(self, "show_update_notification", 
                                       Q_ARG(str, latest_version), 
                                       Q_ARG(str, release_notes))
            else:
                logging.info("没有检测到新版本更新")
        except Exception as e:
            logging.error(f"后台版本检查失败: {str(e)}", exc_info=True)
            # 不显示错误给用户，避免影响用户体验
            
    @pyqtSlot(str, str)
    def show_update_notification(self, latest_version, release_notes):
        """显示新版本更新通知"""
        try:
            logging.info(f"显示版本更新通知: {latest_version}")
            
            # 构建更新消息内容
            message = f"发现新版本: {latest_version}\n\n"
            message += f"当前版本: {APP_VERSION}\n\n"
            
            # 添加更新说明（如果有）
            if release_notes:
                # 限制更新说明的长度，避免弹窗过大
                if len(release_notes) > 500:
                    release_notes = release_notes[:500] + "..."
                message += "更新内容:\n" + release_notes + "\n\n"
            else:
                message += "建议更新到最新版本以获取更好的体验。\n\n"
            
            # 创建消息框
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("发现新版本")
            msg_box.setText(message)
            msg_box.setIcon(QMessageBox.Information)
            
            # 设置消息框样式，使其与应用程序风格一致
            msg_box.setStyleSheet(ModernUIComponents.get_stylesheet())
            
            # 添加按钮
            msg_box.addButton("立即查看", QMessageBox.AcceptRole)
            msg_box.addButton("稍后提醒", QMessageBox.RejectRole)
            
            # 显示消息框并处理用户选择
            result = msg_box.exec_()
            
            if result == QMessageBox.AcceptRole:
                # 用户点击了"立即查看"，打开Gitee仓库页面
                try:
                    owner = "seven798"  # Gitee用户名
                    repo = "sora2"  # 仓库名
                    repo_url = f"https://gitee.com/{owner}/{repo}/releases"
                    
                    # 尝试使用QDesktopServices打开链接
                    from PyQt5.QtGui import QDesktopServices
                    from PyQt5.QtCore import QUrl
                    
                    logging.info(f"正在打开Gitee仓库更新页面: {repo_url}")
                    success = QDesktopServices.openUrl(QUrl(repo_url))
                    
                    if success:
                        logging.info(f"成功打开Gitee仓库更新页面")
                    else:
                        raise Exception("QDesktopServices.openUrl返回失败")
                        
                except Exception as e:
                    logging.error(f"打开仓库页面失败: {str(e)}", exc_info=True)
                    # 显示错误消息，但不中断应用
                    try:
                        QMessageBox.warning(self, "操作失败", "无法打开浏览器，请手动访问Gitee仓库查看更新。")
                    except Exception as msg_err:
                        logging.error(f"显示错误消息框失败: {str(msg_err)}", exc_info=True)
                    
        except Exception as e:
            logging.error(f"显示更新通知失败: {str(e)}", exc_info=True)
            # 记录错误但不显示给用户，避免影响用户体验
        
    def setup_status_bar(self):
        """设置状态栏"""
        # 清除现有的状态栏部件，避免重复添加
        for widget in self.statusBar().findChildren(QLabel):
            self.statusBar().removeWidget(widget)
            widget.deleteLater()
        
        self.statusBar().showMessage("就绪")
        self.statusBar().setStyleSheet("background-color: #f0f0f0; color: #333;")
        
        # 添加状态信息标签
        self.status_label = QLabel()
        self.statusBar().addPermanentWidget(self.status_label)
        self.update_status_info()

    def load_config(self):
        try:
            if os.path.exists('sora_app_config.json'):
                with open('sora_app_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.api_key = config.get('api_key', '')
                    self.base_url = config.get('base_url', 'https://api.sora2.email')
                    self.output_dir = config.get('output_dir', '')
                    
                if self.api_key:
                    self.generator = SoraVideoGenerator(self.api_key, self.base_url)
        except Exception as e:
            logging.error(f"加载配置失败: {e}")
            
    def compare_versions(self, v1, v2):
        """比较两个版本号，返回True如果v1 > v2"""
        try:
            # 分割版本号为数字部分
            v1_parts = [int(part) for part in v1.split('.')]
            v2_parts = [int(part) for part in v2.split('.')]
            
            # 比较每个部分
            for i in range(max(len(v1_parts), len(v2_parts))):
                v1_num = v1_parts[i] if i < len(v1_parts) else 0
                v2_num = v2_parts[i] if i < len(v2_parts) else 0
                
                if v1_num > v2_num:
                    return True
                elif v1_num < v2_num:
                    return False
            
            # 所有部分都相等
            return False
        except Exception:
            # 如果解析失败，使用简单的字符串比较作为后备
            return v1 > v2
            
    def check_latest_version(self):
        """从Gitee检查最新版本"""
        # Gitee仓库信息
        owner = "seven798"  # Gitee用户名
        repo = "sora2"  # 仓库名
        
        try:
            # 构造Gitee API URL
            url = f"https://gitee.com/api/v5/repos/{owner}/{repo}/releases/latest"
            logging.info(f"正在检查Gitee仓库最新版本: {url}")
            
            # 发送请求获取最新版本信息
            headers = {
                'Accept': 'application/json',
                'User-Agent': f'SoraVideoApp/{APP_VERSION}'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # 检查请求是否成功
            
            latest_release = response.json()
            latest_version = latest_release.get('tag_name', 'v0.0.0')
            logging.info(f"获取到最新版本标签: {latest_version}")
            
            # 清理版本号（移除可能的前缀）
            if latest_version.startswith('v'):
                latest_version = latest_version[1:]
                
            # 清理当前版本号
            current_version = APP_VERSION[1:] if APP_VERSION.startswith('v') else APP_VERSION
            
            # 比较版本号
            has_update = self.compare_versions(latest_version, current_version)
            
            if has_update:
                release_notes = latest_release.get('body', '')
                logging.info(f"发现新版本: v{latest_version}")
                logging.debug(f"新版本更新内容: {release_notes[:100]}...")
                return f"v{latest_version}", release_notes
            else:
                logging.info(f"当前已是最新版本: {APP_VERSION}")
                return None, None
                
        except requests.exceptions.RequestException as e:
            logging.error(f"网络请求失败: {str(e)}", exc_info=True)
            return None, None
        except json.JSONDecodeError as e:
            logging.error(f"解析响应数据失败: {str(e)}", exc_info=True)
            return None, None
        except Exception as e:
            logging.error(f"检查版本失败: {str(e)}", exc_info=True)
            return None, None
    
    def init_ui(self):
        # 设置窗口标题和尺寸
        self.setWindowTitle("Sora2 视频生成工具")
        
        # 设置更现代的窗口尺寸，确保足够的工作空间
        self.resize(1024, 768)
        
        # 居中显示窗口
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
        # 创建主布局容器
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)  # 设置外边距
        main_layout.setSpacing(10)  # 设置组件间距
        
        # 创建标签页，并应用现代样式
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabShape(QTabWidget.Rounded)
        self.tab_widget.setElideMode(Qt.ElideRight)
        self.tab_widget.setUsesScrollButtons(True)
        
        # 创建各个功能标签页，使用卡片式布局
        self.text_to_video_tab = TextToVideoTab(self)
        self.image_to_video_tab = ImageToVideoTab(self)
        self.task_manager_tab = TaskManagerTab(self)
        self.settings_tab = SettingsTab(self)
        self.web_view_tab = WebViewTab(self)
        
        # 添加标签页，使用emoji图标增强视觉效果
        self.tab_widget.addTab(self.text_to_video_tab, "🔄 文生视频")
        self.tab_widget.addTab(self.image_to_video_tab, "🖼️ 图生视频")
        self.tab_widget.addTab(self.task_manager_tab, "📋 任务管理")
        self.tab_widget.addTab(self.settings_tab, "⚙️ 设置")
        self.tab_widget.addTab(self.web_view_tab, "🌐 额度查询")
        
        # 添加标签页到主布局
        main_layout.addWidget(self.tab_widget, 1)  # 1表示垂直拉伸因子
        
        # 设置中央部件
        self.setCentralWidget(main_widget)
        
        # 设置任务管理器引用
        self.task_manager = self.task_manager_tab
        
        # 优化整体视觉效果
        self.setStyleSheet("""
            QMainWindow {{
                background-color: {bg_color};
            }}
            QTabWidget {{
                background-color: transparent;
            }}
        """.format(bg_color=ModernUIComponents.rgb_to_hex(ModernUIComponents.BACKGROUND_COLOR)))
    
    @property
    def task_manager(self):
        return self._task_manager
    
    @task_manager.setter
    def task_manager(self, manager):
        self._task_manager = manager
    
    def update_status_info(self):
        """更新状态栏信息"""
        if self.api_key:
            self.status_label.setText("已配置API")
        else:
            self.status_label.setText("未配置API")
    
    def show_message(self, message, duration=3000):
        """显示临时消息"""
        self.statusBar().showMessage(message, duration)

# 创建中文菜单的函数
def setup_chinese_context_menu(widget):
    """
    为文本输入控件设置中文右键菜单
    """
    # 创建自定义菜单
    def show_context_menu(pos):
        # 创建右键菜单
        menu = QMenu(widget)
        
        # 创建中文菜单项
        undo_action = QAction("撤销", widget)
        undo_action.setShortcut("Ctrl+Z")
        redo_action = QAction("重做", widget)
        redo_action.setShortcut("Ctrl+Y")
        cut_action = QAction("剪切", widget)
        cut_action.setShortcut("Ctrl+X")
        copy_action = QAction("复制", widget)
        copy_action.setShortcut("Ctrl+C")
        paste_action = QAction("粘贴", widget)
        paste_action.setShortcut("Ctrl+V")
        delete_action = QAction("删除", widget)
        delete_action.setShortcut("Del")
        select_all_action = QAction("全选", widget)
        select_all_action.setShortcut("Ctrl+A")
        
        # 添加菜单项到菜单
        menu.addAction(undo_action)
        menu.addAction(redo_action)
        menu.addSeparator()
        menu.addAction(cut_action)
        menu.addAction(copy_action)
        menu.addAction(paste_action)
        menu.addAction(delete_action)
        menu.addSeparator()
        menu.addAction(select_all_action)
        
        # 连接动作到对应功能
        try:
            # 添加异常处理，确保即使某些方法不可用也能正常工作
            if hasattr(widget, 'undo'):
                undo_action.triggered.connect(widget.undo)
            else:
                undo_action.setEnabled(False)
                
            if hasattr(widget, 'redo'):
                redo_action.triggered.connect(widget.redo)
            else:
                redo_action.setEnabled(False)
                
            if hasattr(widget, 'cut'):
                cut_action.triggered.connect(widget.cut)
            else:
                cut_action.setEnabled(False)
                
            if hasattr(widget, 'copy'):
                copy_action.triggered.connect(widget.copy)
            else:
                copy_action.setEnabled(False)
                
            if hasattr(widget, 'paste'):
                paste_action.triggered.connect(widget.paste)
            else:
                paste_action.setEnabled(False)
                
            if hasattr(widget, 'del_'):
                delete_action.triggered.connect(widget.del_)
            elif hasattr(widget, 'clear'):
                delete_action.triggered.connect(widget.clear)
            else:
                delete_action.setEnabled(False)
                
            if hasattr(widget, 'selectAll'):
                select_all_action.triggered.connect(widget.selectAll)
            else:
                select_all_action.setEnabled(False)
        except Exception as e:
            logging.error(f"连接菜单动作时出错: {str(e)}")
        
        # 更新菜单项状态
        try:
            if hasattr(widget, 'isUndoAvailable'):
                undo_action.setEnabled(widget.isUndoAvailable())
            
            if hasattr(widget, 'isRedoAvailable'):
                redo_action.setEnabled(widget.isRedoAvailable())
        except Exception as e:
            logging.error(f"更新菜单状态时出错: {str(e)}")
        
        # 检查是否有文本被选中
        has_selection = False
        try:
            if hasattr(widget, 'textCursor'):
                has_selection = widget.textCursor().hasSelection()
            elif hasattr(widget, 'selectedText'):
                has_selection = bool(widget.selectedText())
            elif hasattr(widget, 'hasSelectedText'):
                has_selection = widget.hasSelectedText()
        except Exception as e:
            logging.error(f"检查文本选择时出错: {str(e)}")
            
        cut_action.setEnabled(has_selection)
        copy_action.setEnabled(has_selection)
        delete_action.setEnabled(has_selection)
        
        # 显示菜单
        try:
            menu.exec_(widget.mapToGlobal(pos))
        except Exception as e:
            logging.error(f"显示菜单时出错: {str(e)}")
    
    # 替换上下文菜单事件处理器
    try:
        widget.setContextMenuPolicy(Qt.CustomContextMenu)
        widget.customContextMenuRequested.connect(show_context_menu)
        logging.info(f"已为控件 {type(widget).__name__} 设置中文右键菜单")
    except Exception as e:
        logging.error(f"设置右键菜单时出错: {str(e)}")

# 创建自定义的中文输入框类
class ChineseLineEdit(ModernLineEdit):
    """自动使用中文右键菜单的现代风格QLineEdit"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setup_chinese_context_menu(self)

class ChineseTextEdit(ModernTextEdit):
    """自动使用中文右键菜单的现代风格QTextEdit"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setup_chinese_context_menu(self)

# 重命名自定义类为原始类名，这样应用中所有使用QLineEdit和QTextEdit的地方都会自动使用中文菜单版本
QLineEdit = ChineseLineEdit
QTextEdit = ChineseTextEdit

def main():
    import time
    logging.info("开始启动应用程序")
    
    # 为QtWebEngine设置必要的属性
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    
    # 启用高DPI支持
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 设置中文语言环境
    from PyQt5.QtCore import QLocale
    QLocale.setDefault(QLocale(QLocale.Chinese, QLocale.China))
    logging.info("中文语言环境设置完成")
    
    # 设置应用样式为Fusion，这是一个跨平台的现代样式
    app.setStyle('Fusion')
    logging.info("应用样式设置完成")
    
    # 应用全局现代样式表
    stylesheet = ModernUIComponents.get_stylesheet()
    app.setStyleSheet(stylesheet)
    logging.info("全局样式表应用完成")
    
    # 设置全局字体
    font = QFont()
    font.setFamily("微软雅黑")
    font.setPointSize(9)
    app.setFont(font)
    logging.info("全局字体设置完成")

    try:
        # 创建主窗口
        window = SoraVideoApp()
        logging.info("主窗口创建完成")
        
        # 显示窗口
        window.show()
        logging.info("主窗口显示完成")
            
        # 增加窗口的显示优先级
        window.raise_()
        window.activateWindow()      
        
        # 设置窗口的属性，使其具有现代外观
        window.setWindowFlags(window.windowFlags() | Qt.WindowMinMaxButtonsHint)
        
        logging.info("开始应用程序事件循环")
        result = app.exec_()
        logging.info(f"应用程序事件循环结束，返回码: {result}")
        sys.exit(result)
    except Exception as e:
        logging.error(f"应用程序运行出错: {str(e)}", exc_info=True)
        # 显示错误对话框
        error_app = QApplication([])  # 创建一个新的应用实例来显示错误
        QMessageBox.critical(None, "应用程序错误", f"应用程序启动失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
