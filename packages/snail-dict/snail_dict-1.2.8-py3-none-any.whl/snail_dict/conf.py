import logging
import appdirs
from pathlib import Path
import snail_dict

# Meta
NAME = "snail-dict"
VERSION = snail_dict.__version__
AUTHOR = snail_dict.__author__

# Paths
DATA_DIR = Path(appdirs.user_data_dir(NAME, VERSION))
CONFIG_DIR = Path(appdirs.user_config_dir(NAME, VERSION))
CACHE_DIR = Path(appdirs.user_cache_dir(NAME, VERSION))

DATA_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "dictionary.db"
CONFIG_PATH = CONFIG_DIR / "conf.json"
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "configs" / "conf.json"
LOG_FILE = CACHE_DIR / "snail_dict.log"

PROJECT_DIR = Path(__file__).parent.parent
RES_DIR = PROJECT_DIR / "res"


LOG = logging.getLogger("snail_dict")
LOG.setLevel(logging.DEBUG)
_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_file_handler = logging.FileHandler(filename=str(LOG_FILE))
_file_handler.setFormatter(_formatter)
_stderr_handler = logging.StreamHandler()
_stderr_handler.setFormatter(_formatter)
LOG.addHandler(_file_handler)
LOG.addHandler(_stderr_handler)
