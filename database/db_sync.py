from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from models.agent_model import Base, AgentModel
from config.settings import SQLALCHEMY_DATABASE_URL

class DatabaseSync:
    """数据库结构同步管理器"""
    
    def __init__(self):
        self.engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def sync_database(self):
        """同步数据库结构"""
        print("开始同步数据库结构...")
        
        # 1. 创建基础表结构
        Base.metadata.create_all(self.engine)
        
        # 2. 检查并添加缺失的字段
        self._check_and_add_missing_columns()
        
        # 3. 检查并添加缺失的约束
        self._check_and_add_missing_constraints()
        
        print("数据库结构同步完成！")
    
    def _check_and_add_missing_columns(self):
        """检查并添加缺失的列"""
        inspector = inspect(self.engine)
        
        if 'agents' in inspector.get_table_names():
            existing_columns = [col['name'] for col in inspector.get_columns('agents')]
            
            # 检查key字段
            if 'key' not in existing_columns:
                self._add_column('agents', 'key', 'VARCHAR(64) UNIQUE NOT NULL DEFAULT \'default_key\'')
                print("已添加key字段")
            
            # 可以在这里添加更多字段检查
            # 例如：检查其他新字段是否存在
    
    def _check_and_add_missing_constraints(self):
        """检查并添加缺失的约束"""
        inspector = inspect(self.engine)
        
        if 'agents' in inspector.get_table_names():
            # 检查唯一约束
            unique_constraints = inspector.get_unique_constraints('agents')
            key_constraints = [uc['name'] for uc in unique_constraints if 'key' in uc['column_names']]
            
            if not key_constraints:
                # 如果key字段的唯一约束不存在，添加它
                self._add_unique_constraint('agents', 'key', 'uq_agents_key')
                print("已添加key字段的唯一约束")
    
    def _add_column(self, table_name, column_name, column_definition):
        """添加列"""
        with self.engine.connect() as conn:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"))
            conn.commit()
    
    def _add_unique_constraint(self, table_name, column_name, constraint_name):
        """添加唯一约束"""
        with self.engine.connect() as conn:
            conn.execute(text(f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} UNIQUE ({column_name})"))
            conn.commit()
    
    def get_table_info(self):
        """获取表结构信息"""
        inspector = inspect(self.engine)
        
        if 'agents' in inspector.get_table_names():
            print("agents表结构:")
            for column in inspector.get_columns('agents'):
                print(f"  - {column['name']}: {column['type']}")
            
            print("\n约束信息:")
            for constraint in inspector.get_unique_constraints('agents'):
                print(f"  - 唯一约束: {constraint['name']} -> {constraint['column_names']}")

# 全局同步器实例
db_sync = DatabaseSync() 