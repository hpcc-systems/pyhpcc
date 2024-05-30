# Configurations for pyhpcc
import os

## Debug Config
# If the debug env variable exists, set to False else set to True
DEBUG = os.environ.get("DEBUG", False) or True

## Workunit Config
WORKUNIT_STATE_MAP = {'unknown': 0,
                      'compiled': 1,
                      'running': 2,
                      'completed': 3,
                      'failed': 4,
                      'archived': 5,
                      'aborting': 6,
                      'aborted': 7,
                      'blocked': 8,
                      'submitted': 9,
                      'scheduled': 10,
                      'compiling': 11,
                      'wait': 12,
                      'uploadingFiles': 13,
                      'debugPaused': 14,
                      'debugRunning': 15,
                      'paused': 16,
                      'statesize': 17
                      }
