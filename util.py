#!/usr/bin/env python3

import coloredlogs, logging

logger = logging.getLogger(__name__)

coloredlogs.DEFAULT_LEVEL_STYLES = {
    "info"   : {"color": "white"}, 
    "warning": {"color": "yellow"}, 
    "success": {"color": "green"}, 
    "error"  : {"color": "red"}
}

coloredlogs.DEFAULT_FIELD_STYLES = {
    "asctime"  : {"color": "green"}, 
    "hostname" : {"color": "magenta"}, 
    "levelname": {"color": "blue", "bold": True}, 
    "name"     : {"color": "blue"}
}

coloredlogs.install(
    datefmt = "%Y-%m-%d %H:%M:%S",
    fmt = "%(asctime)s %(levelname)s: %(message)s"
)