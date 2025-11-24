# -*- coding: utf-8 -*-
"""
Sora2 视频生成工具
"""

import sys
import os
import json
import time
import uuid
import base64
import requests
from datetime import datetime
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QComboBox, QTextEdit, QProgressBar, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QSplitter,
    QStackedWidget, QListWidget, QListWidgetItem, QInputDialog, QLineEdit
)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor, QPalette, QBrush
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl, QFile, QIODevice, QTextStream, QTimer

# 配置文件路径
CONFIG_FILE = "sora_app_config.json"
TASKS_FILE = "sora_tasks.json"
LOG_FILE = "sora_app.log"

# 默认配置
DEFAULT_CONFIG = {
    "api_base_url": "https://api.sora2.example.com/v1",
    "api_key": "",
    "output_folder": "./dist",
    "max_concurrent_tasks": 2,
    "proxy_enabled": False,
    "proxy_url": ""
}

# 任务状态
TASK_STATUS = {
    "PENDING": "等待中",
    "PROCESSING": "处理中",
    "COMPLETED": "已完成",
    "FAILED": "失败"
}

class LogManager:
    """日志管理器"""
    @staticmethod
    def log(message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # 输出到控制台
        print(log_entry.strip())
        
        # 写入日志文件
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"无法写入日志文件: {e}")

class ConfigManager:
    """配置管理器"""
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    # 合并默认配置
                    for key, value in DEFAULT_CONFIG.items():
                        if key not in config:
                            config[key] = value
                    return config
            return DEFAULT_CONFIG.copy()
        except Exception as e:
            LogManager.log(f"加载配置失败: {e}", "ERROR")
            return DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """保存配置"""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            LogManager.log(f"保存配置失败: {e}", "ERROR")
            return False
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value
        return self.save_config()

class TaskManager:
    """任务管理器"""
    def __init__(self):
        self.tasks = self.load_tasks()
    
    def load_tasks(self):
        """加载任务列表"""
        try:
            if os.path.exists(TASKS_FILE):
                with open(TASKS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            return []
        except Exception as e:
            LogManager.log(f"加载任务失败: {e}", "ERROR")
            return []
    
    def save_tasks(self):
        """保存任务列表"""
        try:
            with open(TASKS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            LogManager.log(f"保存任务失败: {e}", "ERROR")
            return False
    
    def add_task(self, task_data):
        """添加新任务"""
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "created_at": datetime.now().isoformat(),
            "status": TASK_STATUS["PENDING"],
            "progress": 0,
            **task_data
        }
        self.tasks.append(task)
        self.save_tasks()
        return task_id
    
    def update_task(self, task_id, updates):
        """更新任务状态"""
        for task in self.tasks:
            if task["id"] == task_id:
                task.update(updates)
                self.save_tasks()
                return True
        return False
    
    def get_task(self, task_id):
        """获取任务信息"""
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None
    
    def get_tasks(self):
        """获取所有任务"""
        return self.tasks
    
    def delete_task(self, task_id):
        """删除任务"""
        self.tasks = [task for task in self.tasks if task["id"] != task_id]
        self.save_tasks()

class SoraAPIClient:
    """Sora API 客户端"""
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.session = self._create_session()
    
    def _create_session(self):
        """创建会话"""
        session = requests.Session()
        
        # 设置代理
        if self.config_manager.get("proxy_enabled"):
            proxy_url = self.config_manager.get("proxy_url")
            if proxy_url:
                session.proxies = {
                    "http": proxy_url,
                    "https": proxy_url
                }
        
        # 设置默认头
        api_key = self.config_manager.get("api_key")
        if api_key:
            session.headers["Authorization"] = f"Bearer {api_key}"
        
        session.headers["Content-Type"] = "application/json"
        return session
    
    def generate_video(self, prompt, width=1920, height=1080, duration=10, **kwargs):
        """生成视频"""
        try:
            endpoint = f"{self.config_manager.get('api_base_url')}/videos/generate"
            payload = {
                "prompt": prompt,
                "width": width,
                "height": height,
                "duration": duration,
                **kwargs
            }
            
            response = self.session.post(endpoint, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            LogManager.log(f"API调用失败: {e}", "ERROR")
            raise
    
    def get_task_status(self, task_id):
        """获取任务状态"""
        try:
            endpoint = f"{self.config_manager.get('api_base_url')}/tasks/{task_id}"
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            LogManager.log(f"获取任务状态失败: {e}", "ERROR")
            raise

class TaskProcessor(QThread):
    """任务处理线程"""
    progress_updated = pyqtSignal(str, int)
    status_changed = pyqtSignal(str, str)
    task_completed = pyqtSignal(str, dict)
    task_failed = pyqtSignal(str, str)
    
    def __init__(self, task_id, task_data, api_client, task_manager):
        super().__init__()
        self.task_id = task_id
        self.task_data = task_data
        self.api_client = api_client
        self.task_manager = task_manager
        self.running = True
    
    def run(self):
        """运行任务处理"""
        try:
            # 更新任务状态为处理中
            self.status_changed.emit(self.task_id, TASK_STATUS["PROCESSING"])
            self.task_manager.update_task(self.task_id, {"status": TASK_STATUS["PROCESSING"]})
            
            # 调用API生成视频
            LogManager.log(f"开始处理任务: {self.task_id}, 提示词: {self.task_data.get('prompt')}")
            
            # 模拟API调用和进度更新
            for progress in range(0, 101, 10):
                if not self.running:
                    break
                
                self.progress_updated.emit(self.task_id, progress)
                self.task_manager.update_task(self.task_id, {"progress": progress})
                self.msleep(500)  # 模拟处理时间
            
            if not self.running:
                return
            
            # 模拟任务完成
            output_filename = f"{self.task_id[:8]}_output.mp4"
            output_path = os.path.join(self.task_manager.config_manager.get("output_folder"), output_filename)
            
            # 确保输出目录存在
            os.makedirs(self.task_manager.config_manager.get("output_folder"), exist_ok=True)
            
            # 模拟生成视频文件
            with open(output_path, "w") as f:
                f.write("dummy video content")
            
            # 更新任务状态为完成
            result = {
                "output_path": output_path,
                "output_filename": output_filename,
                "generated_at": datetime.now().isoformat()
            }
            
            self.status_changed.emit(self.task_id, TASK_STATUS["COMPLETED"])
            self.task_manager.update_task(self.task_id, {
                "status": TASK_STATUS["COMPLETED"],
                "progress": 100,
                "result": result
            })
            
            self.task_completed.emit(self.task_id, result)
            LogManager.log(f"任务完成: {self.task_id}, 输出文件: {output_filename}")
            
        except Exception as e:
            error_msg = str(e)
            self.status_changed.emit(self.task_id, TASK_STATUS["FAILED"])
            self.task_manager.update_task(self.task_id, {
                "status": TASK_STATUS["FAILED"],
                "error": error_msg
            })
            self.task_failed.emit(self.task_id, error_msg)
            LogManager.log(f"任务失败: {self.task_id}, 错误: {error_msg}", "ERROR")
    
    def stop(self):
        """停止任务处理"""
        self.running = False
        self.wait()

class TaskManagerWidget(QWidget):
    """任务管理界面"""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.task_manager = main_window.task_manager
        self.init_ui()
        self.load_tasks()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 任务列表表格
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(6)
        self.task_table.setHorizontalHeaderLabels(["ID", "类型", "提示词", "状态", "进度", "创建时间"])
        
        # 设置列宽
        header = self.task_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        layout.addWidget(QLabel("任务列表:"))
        layout.addWidget(self.task_table)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("刷新状态")
        self.refresh_button.clicked.connect(self.refresh_tasks)
        
        self.delete_button = QPushButton("删除任务")
        self.delete_button.clicked.connect(self.delete_selected_task)
        
        self.download_button = QPushButton("下载视频")
        self.download_button.clicked.connect(self.download_selected_task)
        
        self.clear_all_button = QPushButton("清除所有任务")
        self.clear_all_button.clicked.connect(self.clear_all_tasks)
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.clear_all_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_tasks(self):
        """加载任务列表"""
        self.task_table.setRowCount(0)
        tasks = self.task_manager.get_tasks()
        
        for task in tasks:
            row_position = self.task_table.rowCount()
            self.task_table.insertRow(row_position)
            
            # 设置任务ID
            task_id_item = QTableWidgetItem(task["id"][:8])
            task_id_item.setData(Qt.UserRole, task["id"])
            self.task_table.setItem(row_position, 0, task_id_item)
            
            # 设置任务类型
            task_type = task.get("task_type", "视频生成")
            self.task_table.setItem(row_position, 1, QTableWidgetItem(task_type))
            
            # 设置提示词
            prompt = task.get("prompt", "")[:50] + ("..." if len(task.get("prompt", "")) > 50 else "")
            self.task_table.setItem(row_position, 2, QTableWidgetItem(prompt))
            
            # 设置状态
            status = task.get("status", TASK_STATUS["PENDING"])
            status_item = QTableWidgetItem(status)
            
            # 根据状态设置颜色
            if status == TASK_STATUS["COMPLETED"]:
                status_item.setBackground(QColor(200, 255, 200))
            elif status == TASK_STATUS["FAILED"]:
                status_item.setBackground(QColor(255, 200, 200))
            elif status == TASK_STATUS["PROCESSING"]:
                status_item.setBackground(QColor(255, 255, 200))
            
            self.task_table.setItem(row_position, 3, status_item)
            
            # 设置进度
            progress = task.get("progress", 0)
            self.task_table.setItem(row_position, 4, QTableWidgetItem(f"{progress}%"))
            
            # 设置创建时间
            created_at = task.get("created_at", "")
            # 格式化时间
            try:
                dt = datetime.fromisoformat(created_at)
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                formatted_time = created_at
            
            self.task_table.setItem(row_position, 5, QTableWidgetItem(formatted_time))
    
    def refresh_tasks(self):
        """刷新任务列表"""
        self.load_tasks()
        QMessageBox.information(self, "刷新成功", "任务列表已刷新")
    
    def delete_selected_task(self):
        """删除选中的任务"""
        selected_rows = set()
        for item in self.task_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要删除的任务")
            return
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除选中的 {len(selected_rows)} 个任务吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 按行号降序删除，避免索引问题
            for row in sorted(selected_rows, reverse=True):
                task_id = self.task_table.item(row, 0).data(Qt.UserRole)
                self.task_manager.delete_task(task_id)
                self.task_table.removeRow(row)
            
            QMessageBox.information(self, "删除成功", "任务已删除")
    
    def download_selected_task(self):
        """下载选中任务的视频"""
        selected_row = self.task_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要下载的任务")
            return
        
        task_id = self.task_table.item(selected_row, 0).data(Qt.UserRole)
        task = self.task_manager.get_task(task_id)
        
        if not task or task.get("status") != TASK_STATUS["COMPLETED"]:
            QMessageBox.warning(self, "警告", "只能下载已完成的任务视频")
            return
        
        result = task.get("result", {})
        output_filename = result.get("output_filename")
        if not output_filename:
            QMessageBox.warning(self, "错误", "找不到输出文件名")
            return
        
        # 打开文件保存对话框
        save_path, _ = QFileDialog.getSaveFileName(
            self, "保存视频文件", 
            os.path.join(os.path.expanduser("~"), output_filename),
            "视频文件 (*.mp4)"
        )
        
        if save_path:
            try:
                # 复制文件
                import shutil
                source_path = result.get("output_path")
                if os.path.exists(source_path):
                    shutil.copy2(source_path, save_path)
                    QMessageBox.information(self, "下载成功", f"视频已保存到: {save_path}")
                else:
                    QMessageBox.warning(self, "错误", "源文件不存在")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"保存文件失败: {str(e)}")
    
    def clear_all_tasks(self):
        """清除所有任务"""
        reply = QMessageBox.question(
            self, "确认清除", 
            "确定要清除所有任务吗？此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 清除任务管理器中的所有任务
            for task in self.task_manager.get_tasks()[:]:
                self.task_manager.delete_task(task["id"])
            
            # 清空表格
            self.task_table.setRowCount(0)
            QMessageBox.information(self, "清除成功", "所有任务已清除")

class SettingsWidget(QWidget):
    """设置界面"""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.config_manager = main_window.config_manager
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # API 设置组
        api_group = QGroupBox("API 设置")
        api_layout = QVBoxLayout()
        
        # API URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("API 基础URL:"))
        self.api_url_input = QLineEdit()
        url_layout.addWidget(self.api_url_input)
        api_layout.addLayout(url_layout)
        
        # API Key
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        key_layout.addWidget(self.api_key_input)
        api_layout.addLayout(key_layout)
        
        # 输出文件夹
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出文件夹:"))
        self.output_folder_input = QLineEdit()
        output_layout.addWidget(self.output_folder_input)
        
        self.browse_button = QPushButton("浏览...")
        self.browse_button.clicked.connect(self.browse_output_folder)
        output_layout.addWidget(self.browse_button)
        api_layout.addLayout(output_layout)
        
        # 最大并发任务数
        concurrent_layout = QHBoxLayout()
        concurrent_layout.addWidget(QLabel("最大并发任务数:"))
        self.concurrent_tasks_input = QComboBox()
        self.concurrent_tasks_input.addItems(["1", "2", "3", "4", "5"])
        concurrent_layout.addWidget(self.concurrent_tasks_input)
        api_layout.addLayout(concurrent_layout)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # 代理设置组
        proxy_group = QGroupBox("代理设置")
        proxy_layout = QVBoxLayout()
        
        proxy_check_layout = QHBoxLayout()
        self.proxy_checkbox = QPushButton("启用代理")
        self.proxy_checkbox.setCheckable(True)
        self.proxy_checkbox.clicked.connect(self.toggle_proxy)
        proxy_check_layout.addWidget(self.proxy_checkbox)
        proxy_layout.addLayout(proxy_check_layout)
        
        proxy_url_layout = QHBoxLayout()
        proxy_url_layout.addWidget(QLabel("代理URL:"))
        self.proxy_url_input = QLineEdit()
        self.proxy_url_input.setEnabled(False)
        proxy_url_layout.addWidget(self.proxy_url_input)
        proxy_layout.addLayout(proxy_url_layout)
        
        proxy_group.setLayout(proxy_layout)
        layout.addWidget(proxy_group)
        
        # 保存按钮
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        
        self.save_button = QPushButton("保存设置")
        self.save_button.clicked.connect(self.save_settings)
        save_layout.addWidget(self.save_button)
        
        self.reset_button = QPushButton("恢复默认")
        self.reset_button.clicked.connect(self.reset_settings)
        save_layout.addWidget(self.reset_button)
        
        layout.addLayout(save_layout)
        
        self.setLayout(layout)
    
    def load_settings(self):
        """加载设置"""
        self.api_url_input.setText(self.config_manager.get("api_base_url"))
        self.api_key_input.setText(self.config_manager.get("api_key"))
        self.output_folder_input.setText(self.config_manager.get("output_folder"))
        
        max_concurrent = str(self.config_manager.get("max_concurrent_tasks"))
        if max_concurrent in ["1", "2", "3", "4", "5"]:
            self.concurrent_tasks_input.setCurrentText(max_concurrent)
        
        proxy_enabled = self.config_manager.get("proxy_enabled")
        self.proxy_checkbox.setChecked(proxy_enabled)
        self.proxy_url_input.setEnabled(proxy_enabled)
        self.proxy_url_input.setText(self.config_manager.get("proxy_url"))
    
    def save_settings(self):
        """保存设置"""
        self.config_manager.set("api_base_url", self.api_url_input.text())
        self.config_manager.set("api_key", self.api_key_input.text())
        self.config_manager.set("output_folder", self.output_folder_input.text())
        self.config_manager.set("max_concurrent_tasks", int(self.concurrent_tasks_input.currentText()))
        self.config_manager.set("proxy_enabled", self.proxy_checkbox.isChecked())
        self.config_manager.set("proxy_url", self.proxy_url_input.text())
        
        QMessageBox.information(self, "保存成功", "设置已保存")
    
    def reset_settings(self):
        """恢复默认设置"""
        reply = QMessageBox.question(
            self, "确认重置", 
            "确定要恢复默认设置吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config_manager.config = DEFAULT_CONFIG.copy()
            self.config_manager.save_config()
            self.load_settings()
            QMessageBox.information(self, "重置成功", "设置已恢复为默认值")
    
    def browse_output_folder(self):
        """浏览输出文件夹"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "选择输出文件夹",
            self.output_folder_input.text() or os.path.expanduser("~")
        )
        
        if folder_path:
            self.output_folder_input.setText(folder_path)
    
    def toggle_proxy(self):
        """切换代理启用状态"""
        self.proxy_url_input.setEnabled(self.proxy_checkbox.isChecked())

class VideoGenerationWidget(QWidget):
    """视频生成界面"""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.task_manager = main_window.task_manager
        self.api_client = main_window.api_client
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 提示词输入
        prompt_layout = QVBoxLayout()
        prompt_layout.addWidget(QLabel("提示词 (详细描述您想要生成的视频内容):"))
        self.prompt_text = QTextEdit()
        self.prompt_text.setPlaceholderText("例如: 一只小猫在阳光下玩耍...")
        self.prompt_text.setMinimumHeight(100)
        prompt_layout.addWidget(self.prompt_text)
        
        # 视频参数
        params_layout = QVBoxLayout()
        params_layout.addWidget(QLabel("视频参数:"))
        
        # 分辨率选择
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("分辨率:"))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "1920x1080 (1080p)",
            "1280x720 (720p)", 
            "854x480 (480p)",
            "640x360 (360p)"
        ])
        resolution_layout.addWidget(self.resolution_combo)
        params_layout.addLayout(resolution_layout)
        
        # 时长选择
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("时长 (秒):"))
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["10", "20", "30", "60"])
        duration_layout.addWidget(self.duration_combo)
        params_layout.addLayout(duration_layout)
        
        # 高级设置折叠面板（这里简化实现）
        advanced_group = QGroupBox("高级设置 (可选)")
        advanced_layout = QVBoxLayout()
        
        # 视频风格
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("视频风格:"))
        self.style_combo = QComboBox()
        self.style_combo.addItems(["默认", "写实", "动画", "卡通", "油画", "水彩"])
        style_layout.addWidget(self.style_combo)
        advanced_layout.addLayout(style_layout)
        
        # 帧率
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("帧率:"))
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["24", "30", "60"])
        fps_layout.addWidget(self.fps_combo)
        advanced_layout.addLayout(fps_layout)
        
        advanced_group.setLayout(advanced_layout)
        params_layout.addWidget(advanced_group)
        
        # 生成按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.generate_button = QPushButton("开始生成视频")
        self.generate_button.setMinimumHeight(40)
        self.generate_button.clicked.connect(self.start_generation)
        button_layout.addWidget(self.generate_button)
        
        # 布局组合
        layout.addLayout(prompt_layout)
        layout.addLayout(params_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def start_generation(self):
        """开始生成视频"""
        # 获取提示词
        prompt = self.prompt_text.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "警告", "请输入提示词")
            return
        
        # 检查API Key
        if not self.main_window.config_manager.get("api_key"):
            QMessageBox.warning(self, "警告", "请先在设置中配置API Key")
            self.main_window.show_settings_tab()
            return
        
        # 获取参数
        resolution = self.resolution_combo.currentText().split(" ")[0]
        width, height = map(int, resolution.split("x"))
        duration = int(self.duration_combo.currentText())
        style = self.style_combo.currentText() if self.style_combo.currentText() != "默认" else None
        fps = int(self.fps_combo.currentText())
        
        # 构建任务数据
        task_data = {
            "task_type": "视频生成",
            "prompt": prompt,
            "width": width,
            "height": height,
            "duration": duration,
            "fps": fps
        }
        
        if style:
            task_data["style"] = style
        
        # 添加任务
        task_id = self.task_manager.add_task(task_data)
        
        # 创建并启动任务处理器
        task_processor = TaskProcessor(
            task_id, task_data, self.api_client, self.task_manager
        )
        
        # 连接信号
        task_processor.progress_updated.connect(self.update_task_progress)
        task_processor.status_changed.connect(self.update_task_status)
        task_processor.task_completed.connect(self.on_task_completed)
        task_processor.task_failed.connect(self.on_task_failed)
        
        # 保存任务处理器引用
        self.main_window.active_tasks[task_id] = task_processor
        
        # 启动任务
        task_processor.start()
        
        # 切换到任务管理标签
        self.main_window.show_tasks_tab()
        
        QMessageBox.information(self, "任务已创建", f"视频生成任务已创建，任务ID: {task_id[:8]}")
    
    def update_task_progress(self, task_id, progress):
        """更新任务进度"""
        # 这个方法会被信号调用，但实际的UI更新会在TaskManagerWidget中处理
        pass
    
    def update_task_status(self, task_id, status):
        """更新任务状态"""
        # 这个方法会被信号调用，但实际的UI更新会在TaskManagerWidget中处理
        pass
    
    def on_task_completed(self, task_id, result):
        """任务完成处理"""
        # 从活跃任务中移除
        if task_id in self.main_window.active_tasks:
            del self.main_window.active_tasks[task_id]
        
        # 通知用户
        QMessageBox.information(
            self, 
            "生成完成", 
            f"视频生成成功！\n文件名: {result.get('output_filename')}"
        )
    
    def on_task_failed(self, task_id, error_msg):
        """任务失败处理"""
        # 从活跃任务中移除
        if task_id in self.main_window.active_tasks:
            del self.main_window.active_tasks[task_id]
        
        # 通知用户
        QMessageBox.warning(
            self, 
            "生成失败", 
            f"视频生成失败！\n错误信息: {error_msg}"
        )

class Sora2App(QMainWindow):
    """Sora2视频生成工具主窗口"""
    def __init__(self):
        super().__init__()
        # 初始化管理器
        self.config_manager = ConfigManager()
        self.task_manager = TaskManager()
        self.api_client = SoraAPIClient(self.config_manager)
        self.active_tasks = {}
        
        # 初始化UI
        self.init_ui()
        
        # 确保输出目录存在
        os.makedirs(self.config_manager.get("output_folder"), exist_ok=True)
    
    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口标题和尺寸
        self.setWindowTitle("Sora2 视频生成工具")
        self.setGeometry(100, 100, 1000, 700)
        
        # 设置图标
        if os.path.exists("icon.ico"):
            self.setWindowIcon(QIcon("icon.ico"))
        
        # 创建中心部件
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # 创建选项卡
        self.tabs = QStackedWidget()
        
        # 创建各个界面
        self.video_gen_widget = VideoGenerationWidget(self)
        self.tasks_widget = TaskManagerWidget(self)
        self.settings_widget = SettingsWidget(self)
        
        # 添加到选项卡
        self.tabs.addWidget(self.video_gen_widget)
        self.tabs.addWidget(self.tasks_widget)
        self.tabs.addWidget(self.settings_widget)
        
        # 创建导航菜单
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        
        self.nav_home = QPushButton("文生视频")
        self.nav_home.setCheckable(True)
        self.nav_home.setChecked(True)
        self.nav_home.clicked.connect(lambda: self.tabs.setCurrentIndex(0))
        
        self.nav_tasks = QPushButton("任务管理")
        self.nav_tasks.setCheckable(True)
        self.nav_tasks.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
        
        self.nav_settings = QPushButton("设置")
        self.nav_settings.setCheckable(True)
        self.nav_settings.clicked.connect(lambda: self.tabs.setCurrentIndex(2))
        
        # 设置按钮组样式
        button_group = [self.nav_home, self.nav_tasks, self.nav_settings]
        for btn in button_group:
            btn.setMinimumHeight(40)
            btn.setStyleSheet("QPushButton:checked { background-color: #4CAF50; color: white; }")
            nav_layout.addWidget(btn)
        
        # 连接按钮点击信号，实现单选效果
        self.nav_home.clicked.connect(lambda: self.set_checked_button(self.nav_home, button_group))
        self.nav_tasks.clicked.connect(lambda: self.set_checked_button(self.nav_tasks, button_group))
        self.nav_settings.clicked.connect(lambda: self.set_checked_button(self.nav_settings, button_group))
        
        # 添加到主布局
        main_layout.addWidget(nav_widget)
        main_layout.addWidget(self.tabs, 1)
        
        # 设置中心部件
        self.setCentralWidget(central_widget)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
    
    def set_checked_button(self, clicked_button, button_group):
        """设置选中的按钮，取消其他按钮的选中状态"""
        for btn in button_group:
            btn.setChecked(btn == clicked_button)
    
    def show_tasks_tab(self):
        """显示任务管理标签"""
        self.tabs.setCurrentIndex(1)
        self.set_checked_button(self.nav_tasks, [self.nav_home, self.nav_tasks, self.nav_settings])
        # 刷新任务列表
        self.tasks_widget.load_tasks()
    
    def show_settings_tab(self):
        """显示设置标签"""
        self.tabs.setCurrentIndex(2)
        self.set_checked_button(self.nav_settings, [self.nav_home, self.nav_tasks, self.nav_settings])
    
    def closeEvent(self, event):
        """关闭窗口时停止所有任务"""
        # 停止所有活跃任务
        for task_id, task_processor in list(self.active_tasks.items()):
            task_processor.stop()
        
        # 确认关闭
        reply = QMessageBox.question(
            self, '确认关闭',
            '确定要关闭应用程序吗？',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

def main():
    """主函数"""
    # 记录启动日志
    LogManager.log("Sora2视频生成工具启动")
    
    # 确保中文显示正常
    font = QFont("SimHei")
    
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setFont(font)
    
    # 创建并显示主窗口
    window = Sora2App()
    window.show()
    
    # 运行应用程序
    try:
        sys.exit(app.exec_())
    except Exception as e:
        LogManager.log(f"应用程序异常退出: {e}", "ERROR")
        sys.exit(1)
    finally:
        LogManager.log("Sora2视频生成工具关闭")

if __name__ == "__main__":
    main()