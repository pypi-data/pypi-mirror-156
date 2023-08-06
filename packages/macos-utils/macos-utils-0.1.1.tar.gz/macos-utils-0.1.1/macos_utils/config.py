#!/usr/bin/env python3

from pathlib import Path

SPOTLIGHT_CONFIG_PLIST_FILE = Path(
    '/System/Volumes/Data/.Spotlight-V100/VolumeConfiguration.plist'
)

SPOTLIGHT_INDEXING_LAUNCHD_SERVICE_NAME = 'com.apple.metadata.mds'
