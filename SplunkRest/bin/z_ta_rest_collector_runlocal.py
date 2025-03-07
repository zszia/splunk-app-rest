import libs as libs

import z_ta_rest_collector
from splunkz import splunk_env

if __name__ == "__main__":
    splunk_env.configure_console_logging()
    z_ta_rest_collector.modular_input.do_run("z_ta_rest_collector://instance")
