# SQLALCHEMY_DATABASE_URI = "sqlite:///self_storage.sqlite"
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://collector:collrest@localhost:3306/collector_rest?charset=utf8mb4"
SQLALCHEMY_ECHO = False
# Absolute Paths
MCF_CONFIG = "TEMP_CONFIG_STORAGE\\MCF_CONFIG_TEMP.yaml" # 主配置文件
TASK_TEMPLATE_CONFIG = "F:\\mcf_xxx.yml" # 子任务配置文件
TEMPORARY_CONFIG_DIR = "TEMP_CONFIG_STORAGE" # 存放每次生成的临时配置文件
MAIN_MCF_REMOTE_CHROME_COMMAND = '/remote;9223 "D:\\selenium_workspace\\remote_ud"'
