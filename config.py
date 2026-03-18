#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件模块
职责：定义所有配置常量、路径、科目列表等全局配置
"""

import os

# =============================================
# 路径配置（使用 os.path.join 和相对路径）
# =============================================

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据目录
DATA_DIR = os.path.join(BASE_DIR, "data")
INPUT_DIR = os.path.join(DATA_DIR, "input")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")

# 文件路径
STUDENTS_FILE = os.path.join(DATA_DIR, "students.json")
LEGACY_FILE = os.path.join(DATA_DIR, "legacy.dat")

# =============================================
# 数据配置
# =============================================

# 科目列表
SUBJECTS = ["语文", "数学", "英语", "物理", "化学"]

# 学号配置
ID_PREFIX = "2023"
ID_START = 1
ID_LENGTH = 8  # 学号总长度

# 分页大小
PAGE_SIZE = 10

# 及格分数线
PASSING_SCORE = 60

# 成绩范围
SCORE_MIN = 0
SCORE_MAX = 100

# 年龄范围
AGE_MIN = 15
AGE_MAX = 30

# =============================================
# 输出文件配置
# =============================================

# 导出文件名
EXPORT_FILENAME = "students_export.csv"
REPORT_FILENAME = "成绩分析报告.md"

# CSV编码
CSV_ENCODING = "utf-8-sig"

# =============================================
# ANSI 颜色代码
# =============================================

COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"
COLOR_BOLD = "\033[1m"
