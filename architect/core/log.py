# coding=utf-8
"""
RoninNetease 统一日志模块。

提供 info / warn / error / debug 四个级别的日志函数，
底层使用 Python 标准库 logging 模块，默认输出到 stdout。

可通过 modConf() 设置 LOG_LEVEL 来控制日志级别：
    DEBUG, INFO, WARNING, ERROR

使用方式:
    from architect.core.log import info, warn, error, debug

    info('Plugin {} loaded', pluginName)
    warn('Geometries should be preloaded before use.')
    error('Failed to register component "{}"', compName)
"""

import logging
import sys

_logger = logging.getLogger()
_logger.setLevel(logging.INFO)

if not _logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter(
        '[%(levelname)-5s] %(message)s'
    ))
    _logger.addHandler(_handler)


def _format_msg(msg, *args):
    """Format message with args. 使用 %-format 避免消息中的 {} 冲突."""
    if args:
        try:
            return msg % args
        except TypeError:
            return msg.format(*args)
    return msg


def info(msg, *args):
    """记录 INFO 级别日志。"""
    _logger.info(_format_msg(msg, *args))


def warn(msg, *args):
    """记录 WARNING 级别日志。"""
    _logger.warning(_format_msg(msg, *args))


def error(msg, *args):
    """记录 ERROR 级别日志。"""
    _logger.error(_format_msg(msg, *args))


def debug(msg, *args):
    """记录 DEBUG 级别日志。"""
    _logger.debug(_format_msg(msg, *args))


def set_level(level):
    """
    设置日志级别。

    :param level: 日志级别名称字符串 ('DEBUG', 'INFO', 'WARNING', 'ERROR')
                  或 logging 常量 (logging.DEBUG, logging.INFO, etc.)
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    _logger.setLevel(level)


def get_logger():
    """获取底层 logging.Logger 实例，用于高级配置（如添加文件 handler）。"""
    return _logger