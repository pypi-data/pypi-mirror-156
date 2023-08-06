# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2021 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************


# Resume Strategy / Old Offline MODE
RESUME_STRATEGY_GET = "get"
RESUME_STRATEGY_GET_OR_CREATE = "get_or_create"
RESUME_STRATEGY_CREATE = "create"

DEPRECATED_OFFLINE_MODE_CREATE = "create"
DEPRECATED_OFFLINE_MODE_APPEND = "append"

DEPRECATED_OFFLINE_MODE_TO_RESUME_STRATEGY_MAP = {
    DEPRECATED_OFFLINE_MODE_APPEND: RESUME_STRATEGY_GET,
    DEPRECATED_OFFLINE_MODE_CREATE: RESUME_STRATEGY_CREATE,
}

# Conda related assets
CONDA_ENV_FILE_NAME = "conda-environment.yml"
CONDA_ENV_ASSET_TYPE = "conda-environment-definition"

CONDA_SPEC_FILE_NAME = "conda-spec.txt"
CONDA_SPEC_ASSET_TYPE = "conda-specification"

CONDA_INFO_FILE_NAME = "conda-info.yml"
CONDA_INFO_ASSET_TYPE = "conda-info"

# The experiment status response keys
STATUS_RESPONSE_IS_ALIVE_BEAT_DURATION_MILLIS = "is_alive_beat_duration_millis"
STATUS_RESPONSE_GPU_MONITOR_INTERVAL_MILLIS = "gpu_monitor_interval_millis"
STATUS_RESPONSE_CPU_MONITOR_INTERVAL_MILLIS = "cpu_monitor_interval_millis"
STATUS_RESPONSE_PARAMETER_UPDATE_INTERVAL_MILLIS = "parameter_update_interval_millis"
STATUS_RESPONSE_PENDING_RPCS = "pending_rpcs"
STATUS_RESPONSE_CODE = "code"
STATUS_RESPONSE_MESSAGE = "msg"
