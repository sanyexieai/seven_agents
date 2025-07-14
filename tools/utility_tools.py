"""
通用工具模块
提供各种实用工具函数，如数据处理、格式转换、验证等
"""

import os
import json
import re
import hashlib
import base64
import time
import random
import string
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
import csv
import yaml
from io import StringIO


class DataProcessor:
    """数据处理工具"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        return text
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """提取邮箱地址"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """提取URL"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        """提取电话号码"""
        phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        matches = re.findall(phone_pattern, text)
        return [''.join(match) for match in matches]
    
    @staticmethod
    def count_words(text: str) -> int:
        """统计单词数量"""
        if not text:
            return 0
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    
    @staticmethod
    def count_chars(text: str, include_spaces: bool = True) -> int:
        """统计字符数量"""
        if not text:
            return 0
        if include_spaces:
            return len(text)
        return len(text.replace(' ', ''))
    
    @staticmethod
    def generate_summary(text: str, max_length: int = 200) -> str:
        """生成文本摘要"""
        if not text:
            return ""
        
        # 简单的摘要生成：取前N个字符
        if len(text) <= max_length:
            return text
        
        # 尝试在句子边界截断
        sentences = re.split(r'[.!?。！？]', text)
        summary = ""
        for sentence in sentences:
            if len(summary + sentence) <= max_length:
                summary += sentence + "."
            else:
                break
        
        # 确保不超过最大长度
        if len(summary) > max_length:
            summary = summary[:max_length]
        
        return summary if summary else text[:max_length] + "..."
    
    @staticmethod
    def detect_language(text: str) -> str:
        """检测文本语言（简化版）"""
        if not text:
            return "unknown"
        
        # 简单的语言检测
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if chinese_chars > 0 and english_chars > 0:
            return "mixed"
        elif chinese_chars > english_chars:
            return "chinese"
        elif english_chars > chinese_chars:
            return "english"
        else:
            return "unknown"


class FileUtils:
    """文件操作工具"""
    
    @staticmethod
    def ensure_directory(path: str) -> bool:
        """确保目录存在"""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"创建目录失败 {path}: {e}")
            return False
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """获取文件信息"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": "文件不存在"}
            
            stat = path.stat()
            return {
                "name": path.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": path.suffix,
                "is_file": path.is_file(),
                "is_directory": path.is_dir()
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def list_files(directory: str, pattern: str = "*") -> List[str]:
        """列出目录中的文件"""
        try:
            directory_path = Path(directory)
            if not directory_path.exists():
                return []
            
            files = list(directory_path.glob(pattern))
            return [str(f) for f in files if f.is_file()]
        except Exception as e:
            print(f"列出文件失败 {directory}: {e}")
            return []
    
    @staticmethod
    def read_file_safe(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """安全读取文件"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            return None
    
    @staticmethod
    def write_file_safe(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """安全写入文件"""
        try:
            # 确保目录存在
            FileUtils.ensure_directory(str(Path(file_path).parent))
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"写入文件失败 {file_path}: {e}")
            return False


class FormatConverter:
    """格式转换工具"""
    
    @staticmethod
    def json_to_yaml(json_str: str) -> str:
        """JSON转YAML"""
        try:
            data = json.loads(json_str)
            return yaml.dump(data, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            return f"转换失败: {e}"
    
    @staticmethod
    def yaml_to_json(yaml_str: str) -> str:
        """YAML转JSON"""
        try:
            data = yaml.safe_load(yaml_str)
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"转换失败: {e}"
    
    @staticmethod
    def csv_to_json(csv_content: str) -> str:
        """CSV转JSON"""
        try:
            lines = csv_content.strip().split('\n')
            if not lines:
                return "[]"
            
            reader = csv.DictReader(lines)
            data = list(reader)
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"转换失败: {e}"
    
    @staticmethod
    def json_to_csv(json_str: str) -> str:
        """JSON转CSV"""
        try:
            data = json.loads(json_str)
            if not data:
                return ""
            
            if isinstance(data, list) and len(data) > 0:
                fieldnames = data[0].keys()
            else:
                return f"转换失败: 数据格式不正确"
            
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
            
            return output.getvalue()
        except Exception as e:
            return f"转换失败: {e}"


class SecurityUtils:
    """安全工具"""
    
    @staticmethod
    def hash_password(password: str, salt: str = None) -> Dict[str, str]:
        """哈希密码"""
        if not salt:
            salt = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        # 使用SHA256哈希
        hash_obj = hashlib.sha256()
        hash_obj.update((password + salt).encode())
        hashed = hash_obj.hexdigest()
        
        return {
            "hash": hashed,
            "salt": salt
        }
    
    @staticmethod
    def verify_password(password: str, hashed: str, salt: str) -> bool:
        """验证密码"""
        hash_result = SecurityUtils.hash_password(password, salt)
        return hash_result["hash"] == hashed
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """生成随机令牌"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def encode_base64(data: str) -> str:
        """Base64编码"""
        return base64.b64encode(data.encode()).decode()
    
    @staticmethod
    def decode_base64(encoded_data: str) -> str:
        """Base64解码"""
        try:
            return base64.b64decode(encoded_data.encode()).decode()
        except Exception:
            return ""


class ValidationUtils:
    """验证工具"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """验证邮箱格式"""
        if not email or '@' not in email:
            return False
        
        # 检查连续的点号
        if '..' in email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """验证电话号码格式"""
        pattern = r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """验证URL格式"""
        pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def is_valid_json(json_str: str) -> bool:
        """验证JSON格式"""
        try:
            json.loads(json_str)
            return True
        except (json.JSONDecodeError, TypeError):
            return False
    
    @staticmethod
    def is_valid_date(date_str: str, format: str = "%Y-%m-%d") -> bool:
        """验证日期格式"""
        # 支持多种日期格式
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d", 
            "%d-%m-%Y",
            "%d/%m/%Y"
        ]
        
        for fmt in formats:
            try:
                datetime.strptime(date_str, fmt)
                return True
            except ValueError:
                continue
        
        return False


class TimeUtils:
    """时间工具"""
    
    @staticmethod
    def get_current_timestamp() -> int:
        """获取当前时间戳"""
        return int(time.time())
    
    @staticmethod
    def timestamp_to_datetime(timestamp: int) -> str:
        """时间戳转日期时间"""
        return datetime.fromtimestamp(timestamp).isoformat()
    
    @staticmethod
    def datetime_to_timestamp(datetime_str: str) -> int:
        """日期时间转时间戳"""
        # 处理ISO格式的日期时间字符串
        if 'T' in datetime_str and 'Z' not in datetime_str and '+' not in datetime_str:
            # 假设是UTC时间
            dt = datetime.fromisoformat(datetime_str + '+00:00')
        else:
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return int(dt.timestamp())
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """格式化持续时间"""
        if seconds < 60:
            return f"{seconds}秒"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}分钟{seconds % 60}秒"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}小时{minutes}分钟"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}天{hours}小时"
    
    @staticmethod
    def get_time_diff(start_time: str, end_time: str) -> str:
        """计算时间差"""
        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            diff = end - start
            return TimeUtils.format_duration(int(diff.total_seconds()))
        except Exception:
            return "时间格式错误"


# 全局工具实例
data_processor = DataProcessor()
file_utils = FileUtils()
format_converter = FormatConverter()
security_utils = SecurityUtils()
validation_utils = ValidationUtils()
time_utils = TimeUtils() 