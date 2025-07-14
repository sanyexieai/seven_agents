"""
通用工具模块的单元测试
"""

import unittest
import tempfile
import os
import sys
import json
import yaml
from unittest.mock import patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.utility_tools import (
    DataProcessor, FileUtils, FormatConverter, SecurityUtils,
    ValidationUtils, TimeUtils
)


class TestDataProcessor(unittest.TestCase):
    """测试数据处理工具"""
    
    def setUp(self):
        self.processor = DataProcessor()
    
    def test_clean_text(self):
        """测试文本清理"""
        dirty_text = "  这是一个  测试文本！@#$%^&*()  \n\n"
        cleaned = self.processor.clean_text(dirty_text)
        
        self.assertEqual(cleaned, "这是一个 测试文本")
    
    def test_clean_empty_text(self):
        """测试清理空文本"""
        self.assertEqual(self.processor.clean_text(""), "")
        self.assertEqual(self.processor.clean_text(None), "")
    
    def test_extract_emails(self):
        """测试提取邮箱"""
        text = "联系邮箱：test@example.com 或者 admin@test.org"
        emails = self.processor.extract_emails(text)
        
        self.assertIn("test@example.com", emails)
        self.assertIn("admin@test.org", emails)
        self.assertEqual(len(emails), 2)
    
    def test_extract_urls(self):
        """测试提取URL"""
        text = "访问网站：https://www.example.com 或者 http://test.org"
        urls = self.processor.extract_urls(text)
        
        self.assertIn("https://www.example.com", urls)
        self.assertIn("http://test.org", urls)
        self.assertEqual(len(urls), 2)
    
    def test_extract_phone_numbers(self):
        """测试提取电话号码"""
        text = "联系电话：123-456-7890 或者 (555) 123-4567"
        phones = self.processor.extract_phone_numbers(text)
        
        self.assertGreater(len(phones), 0)
    
    def test_count_words(self):
        """测试单词计数"""
        text = "这是一个测试文本，包含多个单词。"
        count = self.processor.count_words(text)
        
        self.assertGreater(count, 0)
    
    def test_count_chars(self):
        """测试字符计数"""
        text = "测试文本"
        
        # 包含空格
        count_with_spaces = self.processor.count_chars(text, include_spaces=True)
        self.assertEqual(count_with_spaces, 4)
        
        # 不包含空格
        count_without_spaces = self.processor.count_chars(text, include_spaces=False)
        self.assertEqual(count_without_spaces, 4)
    
    def test_generate_summary(self):
        """测试生成摘要"""
        long_text = "这是第一句话。这是第二句话。这是第三句话。这是第四句话。"
        
        # 测试短摘要
        short_summary = self.processor.generate_summary(long_text, max_length=20)
        self.assertLessEqual(len(short_summary), 20)
        
        # 测试长摘要
        long_summary = self.processor.generate_summary(long_text, max_length=100)
        self.assertEqual(long_summary, long_text)
    
    def test_detect_language(self):
        """测试语言检测"""
        chinese_text = "这是中文文本"
        english_text = "This is English text"
        mixed_text = "这是mixed text"
        
        self.assertEqual(self.processor.detect_language(chinese_text), "chinese")
        self.assertEqual(self.processor.detect_language(english_text), "english")
        self.assertEqual(self.processor.detect_language(mixed_text), "mixed")
        self.assertEqual(self.processor.detect_language(""), "unknown")


class TestFileUtils(unittest.TestCase):
    """测试文件操作工具"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_ensure_directory(self):
        """测试确保目录存在"""
        new_dir = os.path.join(self.temp_dir, "test_dir")
        
        # 创建新目录
        success = FileUtils.ensure_directory(new_dir)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(new_dir))
        
        # 创建已存在的目录
        success = FileUtils.ensure_directory(new_dir)
        self.assertTrue(success)
    
    def test_get_file_info(self):
        """测试获取文件信息"""
        # 创建测试文件
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("测试内容")
        
        info = FileUtils.get_file_info(test_file)
        
        self.assertIn("name", info)
        self.assertIn("size", info)
        self.assertIn("created", info)
        self.assertIn("modified", info)
        self.assertIn("extension", info)
        self.assertIn("is_file", info)
        self.assertIn("is_directory", info)
        
        self.assertEqual(info["name"], "test.txt")
        self.assertEqual(info["extension"], ".txt")
        self.assertTrue(info["is_file"])
        self.assertFalse(info["is_directory"])
    
    def test_get_nonexistent_file_info(self):
        """测试获取不存在文件的信息"""
        info = FileUtils.get_file_info("nonexistent_file.txt")
        self.assertIn("error", info)
    
    def test_list_files(self):
        """测试列出文件"""
        # 创建测试文件
        files = ["test1.txt", "test2.md", "test3.json"]
        for filename in files:
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("测试内容")
        
        # 列出所有文件
        all_files = FileUtils.list_files(self.temp_dir)
        self.assertEqual(len(all_files), 3)
        
        # 列出特定模式的文件
        txt_files = FileUtils.list_files(self.temp_dir, "*.txt")
        self.assertEqual(len(txt_files), 1)
        self.assertTrue(txt_files[0].endswith(".txt"))
    
    def test_list_files_nonexistent_directory(self):
        """测试列出不存在目录的文件"""
        files = FileUtils.list_files("nonexistent_directory")
        self.assertEqual(files, [])
    
    def test_read_file_safe(self):
        """测试安全读取文件"""
        # 创建测试文件
        test_file = os.path.join(self.temp_dir, "test.txt")
        test_content = "测试文件内容"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 读取文件
        content = FileUtils.read_file_safe(test_file)
        self.assertEqual(content, test_content)
    
    def test_read_nonexistent_file_safe(self):
        """测试安全读取不存在的文件"""
        content = FileUtils.read_file_safe("nonexistent_file.txt")
        self.assertIsNone(content)
    
    def test_write_file_safe(self):
        """测试安全写入文件"""
        test_file = os.path.join(self.temp_dir, "write_test.txt")
        test_content = "写入的测试内容"
        
        # 写入文件
        success = FileUtils.write_file_safe(test_file, test_content)
        self.assertTrue(success)
        
        # 验证文件内容
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, test_content)
    
    def test_write_file_safe_with_nonexistent_directory(self):
        """测试写入到不存在目录的文件"""
        test_file = os.path.join(self.temp_dir, "new_dir", "test.txt")
        test_content = "测试内容"
        
        # 应该自动创建目录
        success = FileUtils.write_file_safe(test_file, test_content)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(test_file))


class TestFormatConverter(unittest.TestCase):
    """测试格式转换工具"""
    
    def test_json_to_yaml(self):
        """测试JSON转YAML"""
        json_data = '{"name": "张三", "age": 25, "city": "北京"}'
        yaml_result = FormatConverter.json_to_yaml(json_data)
        
        # 验证YAML格式
        parsed_yaml = yaml.safe_load(yaml_result)
        self.assertEqual(parsed_yaml["name"], "张三")
        self.assertEqual(parsed_yaml["age"], 25)
        self.assertEqual(parsed_yaml["city"], "北京")
    
    def test_json_to_yaml_invalid_json(self):
        """测试无效JSON转YAML"""
        invalid_json = '{"name": "张三", "age": 25,}'
        result = FormatConverter.json_to_yaml(invalid_json)
        
        self.assertIn("转换失败", result)
    
    def test_yaml_to_json(self):
        """测试YAML转JSON"""
        yaml_data = """
name: 张三
age: 25
city: 北京
"""
        json_result = FormatConverter.yaml_to_json(yaml_data)
        
        # 验证JSON格式
        parsed_json = json.loads(json_result)
        self.assertEqual(parsed_json["name"], "张三")
        self.assertEqual(parsed_json["age"], 25)
        self.assertEqual(parsed_json["city"], "北京")
    
    def test_yaml_to_json_invalid_yaml(self):
        """测试无效YAML转JSON"""
        invalid_yaml = """
name: 张三
  age: 25
"""
        result = FormatConverter.yaml_to_json(invalid_yaml)
        
        self.assertIn("转换失败", result)
    
    def test_csv_to_json(self):
        """测试CSV转JSON"""
        csv_data = """name,age,city
张三,25,北京
李四,30,上海"""
        
        json_result = FormatConverter.csv_to_json(csv_data)
        parsed_json = json.loads(json_result)
        
        self.assertEqual(len(parsed_json), 2)
        self.assertEqual(parsed_json[0]["name"], "张三")
        self.assertEqual(parsed_json[0]["age"], "25")
        self.assertEqual(parsed_json[1]["name"], "李四")
        self.assertEqual(parsed_json[1]["age"], "30")
    
    def test_csv_to_json_empty(self):
        """测试空CSV转JSON"""
        result = FormatConverter.csv_to_json("")
        self.assertEqual(result, "[]")
    
    def test_json_to_csv(self):
        """测试JSON转CSV"""
        json_data = '[{"name": "张三", "age": 25}, {"name": "李四", "age": 30}]'
        csv_result = FormatConverter.json_to_csv(json_data)
        
        # 验证CSV格式
        lines = csv_result.strip().split('\n')
        self.assertEqual(len(lines), 3)  # 标题行 + 2数据行
        self.assertIn("name,age", lines[0])
        self.assertIn("张三,25", lines[1])
        self.assertIn("李四,30", lines[2])


class TestSecurityUtils(unittest.TestCase):
    """测试安全工具"""
    
    def test_hash_password(self):
        """测试密码哈希"""
        password = "test_password"
        
        # 使用默认盐值
        result1 = SecurityUtils.hash_password(password)
        self.assertIn("hash", result1)
        self.assertIn("salt", result1)
        
        # 使用自定义盐值
        custom_salt = "custom_salt_123"
        result2 = SecurityUtils.hash_password(password, custom_salt)
        self.assertEqual(result2["salt"], custom_salt)
    
    def test_verify_password(self):
        """测试密码验证"""
        password = "test_password"
        salt = "test_salt"
        
        # 哈希密码
        hash_result = SecurityUtils.hash_password(password, salt)
        
        # 验证正确密码
        self.assertTrue(SecurityUtils.verify_password(password, hash_result["hash"], salt))
        
        # 验证错误密码
        self.assertFalse(SecurityUtils.verify_password("wrong_password", hash_result["hash"], salt))
    
    def test_generate_token(self):
        """测试生成令牌"""
        token1 = SecurityUtils.generate_token(16)
        token2 = SecurityUtils.generate_token(32)
        
        self.assertEqual(len(token1), 16)
        self.assertEqual(len(token2), 32)
        self.assertNotEqual(token1, token2)
    
    def test_encode_decode_base64(self):
        """测试Base64编码解码"""
        original_data = "测试数据"
        
        # 编码
        encoded = SecurityUtils.encode_base64(original_data)
        self.assertIsInstance(encoded, str)
        
        # 解码
        decoded = SecurityUtils.decode_base64(encoded)
        self.assertEqual(decoded, original_data)
    
    def test_decode_invalid_base64(self):
        """测试解码无效的Base64"""
        result = SecurityUtils.decode_base64("invalid_base64!")
        self.assertEqual(result, "")


class TestValidationUtils(unittest.TestCase):
    """测试验证工具"""
    
    def test_is_valid_email(self):
        """测试邮箱验证"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "user+tag@example.co.uk"
        ]
        
        invalid_emails = [
            "invalid_email",
            "@example.com",
            "test@",
            "test..test@example.com"
        ]
        
        for email in valid_emails:
            self.assertTrue(ValidationUtils.is_valid_email(email))
        
        for email in invalid_emails:
            self.assertFalse(ValidationUtils.is_valid_email(email))
    
    def test_is_valid_phone(self):
        """测试电话号码验证"""
        valid_phones = [
            "123-456-7890",
            "(123) 456-7890",
            "+1-123-456-7890"
        ]
        
        invalid_phones = [
            "123",
            "123-456",
            "abc-def-ghij"
        ]
        
        for phone in valid_phones:
            self.assertTrue(ValidationUtils.is_valid_phone(phone))
        
        for phone in invalid_phones:
            self.assertFalse(ValidationUtils.is_valid_phone(phone))
    
    def test_is_valid_url(self):
        """测试URL验证"""
        valid_urls = [
            "https://www.example.com",
            "http://example.org",
            "https://api.example.com/path?param=value"
        ]
        
        invalid_urls = [
            "not_a_url",
            "ftp://example.com",
            "http://"
        ]
        
        for url in valid_urls:
            self.assertTrue(ValidationUtils.is_valid_url(url))
        
        for url in invalid_urls:
            self.assertFalse(ValidationUtils.is_valid_url(url))
    
    def test_is_valid_json(self):
        """测试JSON验证"""
        valid_jsons = [
            '{"name": "test"}',
            '[1, 2, 3]',
            '{"nested": {"key": "value"}}'
        ]
        
        invalid_jsons = [
            '{"name": "test",}',
            '{"name": test}',
            'not json'
        ]
        
        for json_str in valid_jsons:
            self.assertTrue(ValidationUtils.is_valid_json(json_str))
        
        for json_str in invalid_jsons:
            self.assertFalse(ValidationUtils.is_valid_json(json_str))
    
    def test_is_valid_date(self):
        """测试日期验证"""
        valid_dates = [
            "2023-12-31",
            "2023/12/31",
            "31-12-2023"
        ]
        
        invalid_dates = [
            "2023-13-01",  # 无效月份
            "2023-12-32",  # 无效日期
            "not a date"
        ]
        
        for date_str in valid_dates:
            self.assertTrue(ValidationUtils.is_valid_date(date_str))
        
        for date_str in invalid_dates:
            self.assertFalse(ValidationUtils.is_valid_date(date_str))


class TestTimeUtils(unittest.TestCase):
    """测试时间工具"""
    
    def test_get_current_timestamp(self):
        """测试获取当前时间戳"""
        timestamp = TimeUtils.get_current_timestamp()
        
        self.assertIsInstance(timestamp, int)
        self.assertGreater(timestamp, 0)
    
    def test_timestamp_to_datetime(self):
        """测试时间戳转日期时间"""
        timestamp = 1640995200  # 2022-01-01 00:00:00
        datetime_str = TimeUtils.timestamp_to_datetime(timestamp)
        
        self.assertIsInstance(datetime_str, str)
        self.assertIn("2022-01-01", datetime_str)
    
    def test_datetime_to_timestamp(self):
        """测试日期时间转时间戳"""
        datetime_str = "2022-01-01T00:00:00"
        timestamp = TimeUtils.datetime_to_timestamp(datetime_str)
        
        self.assertIsInstance(timestamp, int)
        self.assertEqual(timestamp, 1640995200)
    
    def test_format_duration(self):
        """测试格式化持续时间"""
        # 测试秒
        self.assertEqual(TimeUtils.format_duration(30), "30秒")
        
        # 测试分钟
        self.assertEqual(TimeUtils.format_duration(90), "1分钟30秒")
        
        # 测试小时
        self.assertEqual(TimeUtils.format_duration(3661), "1小时1分钟")
        
        # 测试天
        self.assertEqual(TimeUtils.format_duration(90000), "1天1小时")
    
    def test_get_time_diff(self):
        """测试计算时间差"""
        start_time = "2022-01-01T00:00:00"
        end_time = "2022-01-01T01:30:00"
        
        diff = TimeUtils.get_time_diff(start_time, end_time)
        self.assertEqual(diff, "1小时30分钟")
    
    def test_get_time_diff_invalid_format(self):
        """测试无效时间格式的时间差计算"""
        diff = TimeUtils.get_time_diff("invalid", "also_invalid")
        self.assertEqual(diff, "时间格式错误")


if __name__ == '__main__':
    unittest.main() 