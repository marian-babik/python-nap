```
ETF WN-uFM - ETF worker node micro-framework, runs nagios/monitoring plugins
(in parallel) and has configurable set of backends to support publishing of the
results. 

usage: core.py [-h] [--version] [-p POOL_SIZE] [-i PLUGIN_DIR] [-o OUT_DIR]
               [-b BACKEND] [--prefix PREFIX] [--suffix SUFFIX] [-d]
               [-t TIMEOUT] [--backend-timeout B_TIMEOUT]

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -p POOL_SIZE, --pool POOL_SIZE
                        Number of sub-processes to run in parallel (defaults
                        to 2); setting this to 1 implies sequential execution; 
                        setting to 0 will set the pool size according to number
                        of cpu cores available
  -i PLUGIN_DIR, --plugin-directory PLUGIN_DIR
                        Directory containing plugins to execute
  -o OUT_DIR, --output-directory OUT_DIR
                        Directory to store inter-mediate results
  -b BACKEND, --backend BACKEND
                        Backend to execute for each plugin (one of jsonify,
                        http_upload, etc.)
  --prefix PREFIX       Prefix to be added to plugin name
  --suffix SUFFIX       Suffix to be added to plugin name
  -d, --debug           Specify debugging mode
  -t TIMEOUT, --plugin-timeout TIMEOUT
                        Plugin execution timeout
  --backend-timeout B_TIMEOUT
                        Backend execution timeout
                        
ETF WN-uFM can be also run from python via API, e.g.
import wnfm.core

wnfm.core.wn_fm_pool(plugin_dir, out_dir, backend, plugin_timeout=600, pool_size=2,
               prefix=None, suffix=None, backend_timeout=120, extra=None)
               
API docs:
def wn_fm_pool(plugin_dir, out_dir, backend, plugin_timeout=600, pool_size=2,
               prefix=None, suffix=None, backend_timeout=120, extra=None):
    """
    Searches for plugins in the plugin directory, runs them in parallel using a process pool,
    stores results in output directory and calls configured backends to process the
    output directory further. Pool size is configurable and defaults to 2 to ensure
    all plugins will run even if one of them gets blocked. Timeouts for plugin
    and backend execution are supported. Plugin timeout relies on availability of
    subprocess32 module for python 2 (https://github.com/google/python-subprocess32).
    
    :param plugin_dir:  Directory containing plugins to execute
    :param out_dir: Directory to store plugin results (output)
    :param backend: Backend to call after executing plugin
    :param plugin_timeout: Plugin execution timeout (default is 5 minutes)
    :param backend_timeout: Backend execution timeout (default is 2 minutes)
    :param pool_size: Number of plugins to run in parallel (controls size of the process pool, defaults to 2)
    :param prefix: Prefix to add to each plugin name
    :param suffix: Suffix to add to each plugin name
    :param extra: Any extra configuration that will be passed to backend (please use backend name as prefix)
    :return: once the pool can join
    """


```