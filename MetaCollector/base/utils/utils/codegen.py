import os

import numpy as np
import pandas as pd


class CompareUnit:
    """
    数据范围判断工具，基底调用in_my_range来判断一个输入是否在自己的范围内
    """

    def __init__(self, min_v, max_v):
        """

        :param min_v: 最小值
        :param max_v: 最大值
        """
        self.max_ = max_v
        self.min_ = min_v

    def in_my_range(self, other):
        if self.min_ > other.min_:
            return False
        if self.max_ < other.max_:
            return False
        if self.min_ <= other.min_:
            length = abs(other.min_) + abs(other.max_)
            if (self.min_ + length) <= self.max_:
                return True
            else:
                return False


def file2sql_ddl(path: str, sql_output: str = 'gen.sql', code_output: str = 'gen.py', req_nnl: bool = False) -> bool:
    """
    根据给定的文件导出可使用的SQL建表DDL和对应的Sqlalchemy数据构造代码段，目前仅支持MySQL方言，
    导出的ddl需要人工检查和修改需要被替换的部分才能正式使用

    :param path: 参考文件路径，一个带数据和字段名的文件，用于自动推断类型和数值范围
    :param sql_output: sql文件保存的路径
    :param code_output: python代码片段输出路径
    :param req_nnl: 生成的SQL中是否包含NOT NULL约束
    :return: 布尔值
    """
    should_be_str = ['?', 'b', 'B', 'O', 'S', 'a', 'U', 'V']
    should_be_int = ['i', 'u']
    should_be_float = ['f', 'c']
    should_be_time = ['m', 'M']
    not_null_rules = {True: 'NOT NULL', False: ''}
    unsigned_ranges = {
        'TINYINT': CompareUnit(0, 255),
        'SMALLINT': CompareUnit(0, 65535),
        'MEDIUMINT': CompareUnit(0, 16777215),
        'INTEGER': CompareUnit(0, 4294967295),
        'BIGINT': CompareUnit(0, 18446744073709551615)
    }
    ranges = {'TINYINT': CompareUnit(-128, 127),
              'SMALLINT': CompareUnit(-32768, 32767),
              'MEDIUMINT': CompareUnit(-8388608, 8388607),
              'INTEGER': CompareUnit(-2147483648, 2147483647),
              'BIGINT': CompareUnit(-9223372036854775808, 9223372036854775807)
              }

    rules = {'str': should_be_str, 'int': should_be_int, 'float': should_be_float, 'time': should_be_time}

    type_ = (path.split(os.sep)[-1]).split('.')[-1]

    if type_ == 'csv':
        df = pd.read_csv(path, encoding='utf-8')
    elif type_ == 'xlsx':
        df = pd.read_excel(path, engine='openpyxl')
    elif type_ == 'xls':
        df = pd.read_excel(path)
    else:
        raise NotImplementedError("不支持的文件类型：{}".format(type_))

    # 将dtypes转换为键为字段名，值为对应字段类型的字符串的字典
    columns_with_data_types: dict = df.dtypes.to_dict()
    for type_k in columns_with_data_types.keys():
        columns_with_data_types[type_k] = columns_with_data_types[type_k].str

    code_snippets = ["data = {\n"
                     "    'create_time': '#TODO'\n",
                     "}\n\n",
                     "def not_null_or_nan(value):\n",
                     "    try:\n",
                     "        if not np.isnan(value):\n",
                     "            return True\n",
                     "    except TypeError:\n"
                     "        if not pd.isnull(value):\n",
                     "            return True\n",
                     "    return False\n\n"
                     ]

    sql_rows = ['CREATE TABLE IF NOT EXISTS <SHOULD_REPLACE>\n',
                '(\n',
                "    `id`            BIGINT UNSIGNED\n",
                "    PRIMARY KEY AUTO_INCREMENT COMMENT '主键',\n",
                "\n"
                "    `create_time`   DATETIME\n",
                "    NOT NULL DEFAULT '1970-01-01 08:00:00' COMMENT '数据记录时间，仅在插入时更新',\n",
                "\n",
                "    `update_time`   TIMESTAMP\n",
                "    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '数据更新时间，由触发器更新',\n",
                "\n"
                ]

    # 按列扫描
    for index, column_name in enumerate(columns_with_data_types.keys()):
        print("Handling {}\n".format(column_name))
        value = columns_with_data_types[column_name]
        value_type: str = ''

        for key in rules.keys():
            for rule in rules[key]:
                if rule in value:
                    value_type = key
                    break

        enable_comma = True
        if index == len(columns_with_data_types.keys()) - 1:
            enable_comma = False
        comma_ = {True: ',', False: ''}

        # 推断匹配的SQL类型和数据长度，设置默认值和comment
        type_understand = ''

        # 特殊处理
        if value_type == 'float':
            nc = df[column_name].fillna(-1)
            max_than_zero = nc[nc > 0].tolist()
            float_num = list(filter(lambda num: str(num).split('.')[-1] != '0', max_than_zero))
            if len(float_num) == 0:
                value_type = 'int'

        # 正式推断
        if value_type == 'str':
            max_str_length = df[column_name][df[column_name].notna()].map(len).max()
            type_understand = "VARCHAR({})\n    {} DEFAULT '' COMMENT '原始字段名：{}'{}\n\n". \
                format(max_str_length, not_null_rules[req_nnl], column_name, comma_[enable_comma])

        elif value_type == 'float':
            max_float = np.nanmax(df[column_name])
            cut = str(max_float).split('.')
            precision = len(cut[0])
            scale = len(cut[-1])
            # 默认返回decimal
            if '率' in column_name:
                type_understand = "DECIMAL({}, {})\n    {} DEFAULT {} COMMENT '原始字段名：{}'{}\n\n". \
                    format(15, 4, not_null_rules[req_nnl], "0." + "0" * 4, column_name,
                           comma_[enable_comma])
            elif '价' in column_name:
                type_understand = "DECIMAL({}, {})\n    {} DEFAULT {} COMMENT '原始字段名：{}'{}\n\n". \
                    format(15, 2, not_null_rules[req_nnl], "0." + "0" * 2, column_name,
                           comma_[enable_comma])
            else:
                type_understand = "DECIMAL({}, {})\n    {} DEFAULT {} COMMENT '原始字段名：{}'{}\n\n". \
                    format(precision + scale, scale, not_null_rules[req_nnl], "0." + "0" * scale, column_name,
                           comma_[enable_comma])

        elif value_type == 'int':
            max_int = np.nanmax(df[column_name])
            min_int = np.nanmin(df[column_name])
            cv = CompareUnit(min_int, max_int)

            if '价' in column_name:
                type_understand = "DECIMAL({}, {})\n    {} DEFAULT {} COMMENT '原始字段名：{}'{}\n\n". \
                    format(15, 2, not_null_rules[req_nnl], "0." + "0" * 2, column_name,
                           comma_[enable_comma])

            elif min_int >= 0:
                # 当最小值都大于等于0时，默认返回unsigned
                if max_int > 18446744073709551615:
                    raise AssertionError("Max value is {}, out of range.".format(max_int))

                for type_k in unsigned_ranges.keys():
                    if unsigned_ranges[type_k].in_my_range(cv):
                        type_understand = "{} UNSIGNED\n    " \
                                          "{} DEFAULT 0 COMMENT '原始字段名：{}'{}\n\n".format(type_k,
                                                                                         not_null_rules[req_nnl],
                                                                                         column_name,
                                                                                         comma_[enable_comma])
                        break
                # elif max_int <= 255:
                #     type_understand = "TINYINT UNSIGNED\n    {} DEFAULT 0 COMMENT '原始字段名：{}'{}\n\n". \
                #         format(not_null_rules[req_nnl], column_name, comma_[enable_comma])
                # elif 255 < max_int <= 65535:
                #     type_understand = "SMALLINT UNSIGNED\n    {} DEFAULT 0 COMMENT '原始字段名：{}'{}\n\n". \
                #         format(not_null_rules[req_nnl], column_name, comma_[enable_comma])
                # elif 65535 < max_int <= 16777215:
                #     type_understand = "MEDIUMINT UNSIGNED\n   {} DEFAULT 0 COMMENT '原始字段名：{}'{}\n\n". \
                #         format(not_null_rules[req_nnl], column_name, comma_[enable_comma])
                # elif 16777215 < max_int <= 4294967295:
                #     type_understand = "INTEGER UNSIGNED\n    {} DEFAULT 0 COMMENT '原始字段名：{}'{}\n\n". \
                #         format(not_null_rules[req_nnl], column_name, comma_[enable_comma])
                # elif 4294967295 < max_int <= 18446744073709551615:
                #     type_understand = "BIGINT UNSIGNED\n    {} DEFAULT 0 COMMENT '原始字段名：{}'{}\n\n". \
                #         format(not_null_rules[req_nnl], column_name, comma_[enable_comma])
                # else:
                #     raise AssertionError("Max value is {}, out of range.".format(max_int))

            else:
                # 当出现任何最小值为负的值时，返回无unsigned
                if max_int > 9223372036854775807 or min_int < -9223372036854775808:
                    raise AssertionError("Max value is {}, out of range.".format(max_int))

                for type_k in ranges.keys():
                    if ranges[type_k].in_my_range(cv):
                        type_understand = "{}\n    " \
                                          "{} DEFAULT 0 COMMENT '原始字段名：{}'{}\n\n".format(type_k,
                                                                                         not_null_rules[req_nnl],
                                                                                         column_name,
                                                                                         comma_[enable_comma])
                        break
                # elif max_int <= 127 and min_int >= -128:
                #     type_understand = "TINYINT\n    {} DEFAULT 0 COMMENT '原始字段名：{}'{}\n\n". \
                #         format(not_null_rules[req_nnl], column_name, comma_[enable_comma])
                # elif (127 < max_int <= 32767) and (-128 > min_int >= -32768):
                #     type_understand = "SMALLINT\n    {} DEFAULT 0 COMMENT '原始字段名：{}'{}\n\n". \
                #         format(not_null_rules[req_nnl], column_name, comma_[enable_comma])
                # elif (32767 < max_int <= 8388607) and (-32768 < min_int >= -8388608):
                #     type_understand = "MEDIUMINT\n   {} DEFAULT 0 COMMENT '原始字段名：{}'{}\n\n". \
                #         format(not_null_rules[req_nnl], column_name, comma_[enable_comma])
                # elif (8388607 < max_int <= 2147483647) and (-8388608 < min_int <= -2147483648):
                #     type_understand = "INTEGER\n    {} DEFAULT 0 COMMENT '原始字段名：{}'{}\n\n". \
                #         format(not_null_rules[req_nnl], column_name, comma_[enable_comma])
                # elif (2147483647 < max_int <= 9223372036854775807) and (-2147483648 < min_int <= -9223372036854775808):
                #     type_understand = "BIGINT\n    {} DEFAULT 0 COMMENT '原始字段名：{}'{}\n\n". \
                #         format(not_null_rules[req_nnl], column_name, comma_[enable_comma])
                # else:
                #     raise AssertionError("Max value is {}, out of range.".format(max_int))

        elif value_type == 'time':
            type_understand = "DATETIME\n    {} DEFAULT '1970-01-01 08:00:00' COMMENT '原始字段名：{}'{}\n\n". \
                format(not_null_rules[req_nnl], column_name, comma_[enable_comma])

        single_row = "    `g_{}`  {}".format(column_name, type_understand)
        sql_rows.append(single_row)
        # code_snippets.append("    'g_{}': 'XXXX',\n".format(column))
        code_snippets.append(
            "if not_null_or_nan(source_dict['{}']):\n"
            "    data['g_{}'] = source_dict['{}']\nelse:\n    data['g_{}'] = None\n\n".format(
                column_name,
                column_name,
                column_name,
                column_name))

    # 收尾部分
    sql_rows.append(")\n DEFAULT CHARACTER SET utf8mb4\n  COLLATE utf8mb4_unicode_ci\n    COMMENT <REPLACE>;")
    with open(sql_output, 'w', encoding='utf-8') as f:
        f.writelines(sql_rows)

    with open(code_output, 'w', encoding='utf-8') as f1:
        f1.writelines(code_snippets)

    return True


class ValidationUtil(object):
    """
    用来简化对file2sql_ddl的输出结果的人工校验步骤
    """

    def __init__(self, path: str):
        """初始化验证工具，加载数据

        :param path: 文件路径，目前仅支持csv、xls和xlsx格式
        """
        type_ = (path.split(os.sep)[-1]).split('.')[-1]
        if type_ == 'csv':
            self.df = pd.read_csv(path, encoding='utf-8')
        elif type_ == 'xlsx' or type_ == 'xls':
            self.df = pd.read_excel(path, engine='openpyxl')
        else:
            raise NotImplementedError("不支持的文件类型：{}".format(type_))

        self.str_rule = ['?', 'b', 'B', 'O', 'S', 'a', 'U', 'V']
        self.numeric_rule = ['i', 'u', 'f', 'c']
        self.time_rule = ['m', 'M']
        self.type_rules = {'str': self.str_rule, 'num': self.numeric_rule, 'time': self.time_rule}

    @property
    def columns(self) -> list:
        """返回数据的所有列名

        :return: 字符串列表
        """
        return self.df.columns.to_list()

    @property
    def columns_with_types(self) -> dict:
        """返回数据的所有列名和对应的Numpy类型

        :return: 字典
        """
        return self.df.dtypes.to_dict()

    @property
    def columns_with_types_c(self) -> dict:
        """返回数据的所有列名和对应的Numpy类型Array-protocol type strings
            如Int可以用'i', 'u'来表示

        :return: 字典
        """
        columns_with_data_types: dict = self.df.dtypes.to_dict()
        for k in columns_with_data_types.keys():
            columns_with_data_types[k] = columns_with_data_types[k].str
        return columns_with_data_types

    @staticmethod
    def understand_int_type(number) -> str:
        """根据给定的数字自动推断出当使用整型的时候对应哪个MySQL unsigned integer类型

        :param number: 数值，可以为整数或浮点数
        :return: SQL类型的推断结果字符串
        """
        if number <= 255:
            return "TINYINT UNSIGNED"
        elif 255 < number <= 65535:
            return "SMALLINT UNSIGNED"
        elif 65535 < number <= 16777215:
            return "MEDIUMINT UNSIGNED"
        elif 16777215 < number <= 4294967295:
            return "INTEGER UNSIGNED"
        elif 4294967295 < number <= 18446744073709551615:
            return "BIGINT UNSIGNED"
        else:
            raise AssertionError("Max value is {}, out of range.".format(number))

    @staticmethod
    def understand_float_type(number) -> str:
        """根据给定的数字自动推断出当使用浮点数时，对应的Decimal的precision和scale的配置

        :param number: 数值
        :return: SQL类型的推断结果的字符串
        """
        number = float(number)
        cut = str(number).split('.')
        precision = len(cut[0])
        scale = len(cut[-1])
        return "DECIMAL({}, {})".format(precision + scale, scale)

    def __getitem__(self, item):
        return self.df[item]

    def unique(self, column_name) -> list:
        """返回一个列的唯一值的列表

        :param column_name: 列名
        :return:
        """
        return list(self.df[column_name].unique())

    def max_unique(self, column_name):
        """返回该列的最大的唯一值：对于数字来说，返回字面最大的值；对于字符串来说，返回长度最大的值；对于日期时间来说，返回时间戳最大的值

        :param column_name: 字段名
        :return: 任何值
        """
        for rule_key in self.type_rules.keys():
            for rule in self.type_rules[rule_key]:
                if rule in self.columns_with_types_c[column_name]:
                    if rule_key == 'str':
                        field_lengths = self.df[column_name].astype(str).map(len)
                        return self.df.loc[field_lengths.argmax(), column_name]

                    if rule_key == 'num':
                        return np.nanmax(self.unique(column_name))

                    if rule_key == 'time':
                        return max(self.unique(column_name))

        return None
