# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from ctypes import c_bool, c_char_p
import os.path

from contrast.agent.settings import Settings
from contrast.utils.loggers import DEFAULT_LOG_PATH, DEFAULT_LOG_LEVEL
from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


def initialize():
    logger.debug("Initializing agent-lib")
    # This import loads the shared object file. For safety (for now), we only want to do
    # this if the agent-lib is actually going to be used.
    from contrast_agent_lib import lib_contrast

    log_dir = _get_log_dir()
    log_level = _get_log_level()
    lib_contrast.init_with_options(c_bool(True), c_char_p(log_dir), c_char_p(log_level))


def _get_log_dir():
    """
    For now, use the same directory as the agent logger specified in the local config.

    TODO: PYT-2266 This should be updated when we get new log info from TS. We may also
    want to separate this logging config from the agent logger's config.
    """
    agent_log_dir = Settings().config.get("agent.logger.path") or DEFAULT_LOG_PATH
    return bytes(os.path.abspath(os.path.dirname(agent_log_dir)), "utf8")


def _get_log_level():
    """
    TODO: PYT-2266 same as log dir
    """
    agent_log_level = (
        Settings().config.get("agent.logger.level", "").upper() or DEFAULT_LOG_LEVEL
    )
    return bytes(agent_log_level, "utf8")
