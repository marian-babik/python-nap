import argparse
import sys
import os
import logging
import time
import signal
import traceback
from functools import reduce

try:
    from cStringIO import StringIO
except ImportError:
    import io as StringIO

# complex subprocess import
SUBPROCESS_TIMEOUT = False
try:
    from subprocess import TimeoutExpired

    SUBPROCESS_TIMEOUT = True
    import subprocess
except ImportError:
    try:
        import subprocess32 as subprocess

        SUBPROCESS_TIMEOUT = True
    except ImportError:
        SUBPROCESS_TIMEOUT = False
        import subprocess

try:   # adding py2.6 support for subprocess.check_output
    from subprocess import STDOUT, check_output, CalledProcessError
except ImportError:
    STDOUT = subprocess.STDOUT

    def check_output(*popenargs, **kwargs):
        if 'stdout' in kwargs:  # pragma: no cover
            raise ValueError('stdout argument not allowed, it will be overridden.')
        if 'timeout' in kwargs:
            timeout = kwargs['timeout']
            del kwargs['timeout']
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        if SUBPROCESS_TIMEOUT:
            output, _ = process.communicate(timeout=timeout)
        else:
            output, _ = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise subprocess.CalledProcessError(retcode, cmd, output=output)
        return output
    subprocess.check_output = check_output
    # overwrite CalledProcessError due to `output`
    # keyword not being available (in 2.6)


    class CalledProcessError(Exception):
        def __init__(self, returncode, cmd, output=None):
            self.returncode = returncode
            self.cmd = cmd
            self.output = output

        def __str__(self):
            return "Command '%s' returned non-zero exit status %d" % (
                self.cmd, self.returncode)
    subprocess.CalledProcessError = CalledProcessError

import nap

log = logging.getLogger()

NAGIOS_CMD = '/var/nagios/rw/nagios.cmd'


class TimeoutError(Exception):
    pass


def _handle_timeout(signum, frame):
    raise TimeoutError("Backend execution timed out")


def get_status(ret_code):
    status_map = {nap.OK: "OK", nap.WARNING: "WARNING", nap.CRITICAL: "CRITICAL", nap.UNKNOWN: "UNKNOWN"}
    if ret_code in status_map.keys():
        return status_map[ret_code]
    else:
        return "UNKNOWN - plugin return code was %s" % str(ret_code)


def get_code(status):
    code_map = {'OK': nap.OK, 'WARNING': nap.WARNING, 'CRITICAL': nap.CRITICAL, 'UNKNOWN': nap.UNKNOWN}
    if status in code_map.keys():
        return code_map[status]
    else:
        return 255


def sub_process(args, shell=False, dry_run=False, timeout=3600):
    if dry_run:
        log.info("subprocess call: %s" % args)
        return 0, "success from dry-run"
    try:
        if SUBPROCESS_TIMEOUT:
            str_out = subprocess.check_output(args, shell=shell, stderr=subprocess.STDOUT,
                                              stdin=None, timeout=timeout)
        else:
            str_out = subprocess.check_output(args, shell=shell, stderr=subprocess.STDOUT, stdin=None)
    except subprocess.CalledProcessError as e:
        ret_code = e.returncode
        str_out = e.output
    else:
        ret_code = 0
    return ret_code, str_out


class PluginIO(object):
    def __init__(self, metric_name, hostname, command_pipe=None, dry_run=False):
        sys.stdout = self._stdout = StringIO.StringIO()
        sys.stderr = self._stdout
        self._perf_container = list()
        self.metric_name = metric_name
        self.hostname = hostname
        self.summary = "Plugin didn't set summary message"
        self.status = nap.UNKNOWN
        self.command_pipe = command_pipe
        self.dry_run = dry_run

    def add_perf_data(self, label, value, uom='', warn='', crit='', vmin='', vmax=''):
        self._perf_container.append([label, value, uom, warn, crit, vmin, vmax])

    def set_status(self, status, summary=None):
        self.status = status
        self.summary = summary

    def out(self, s):
        self._stdout.write(str(s) + '\n')

    def write(self, s):
        self._stdout.write(s)

    def printf(self, s):
        self.out(s)

    def truncate(self):
        return self._stdout.truncate()

    def seek(self, pos):
        return self._stdout.seek(pos)

    def tell(self):
        return self._stdout.tell()

    def getvalue(self):
        return self._stdout.getvalue()

    def close(self):
        return self._stdout.close()

    def plugin_nagios_out(self):
        sys.stdout.write("%s - %s" % (get_status(self.status), self.summary))
        if self._perf_container:
            sys.stdout.write(" | ")
            for perf_data in self._perf_container:
                sys.stdout.write("%s=%s%s" % (perf_data[0], str(perf_data[1]), str(perf_data[2])))
                sys.stdout.write(";%s" % perf_data[3])
                sys.stdout.write(";%s" % perf_data[4])
                sys.stdout.write(";%s" % perf_data[5])
                sys.stdout.write(";%s" % perf_data[6])
                sys.stdout.write(" ")
        sys.stdout.write("\n")
        sys.stdout.flush()
        sys.stdout.write(str(self._stdout.getvalue()))
        sys.stdout.flush()

    def plugin_check_mk_out(self):
        sys.stdout.write("%s %s " % (str(self.status), self.metric_name.replace(" ", "_")))
        if self._perf_container:
            for perf_data in self._perf_container:
                sys.stdout.write("%s=%s%s" % (perf_data[0], str(perf_data[1]), str(perf_data[2])))
                sys.stdout.write(";%s" % perf_data[3])
                sys.stdout.write(";%s" % perf_data[4])
                sys.stdout.write(";%s" % perf_data[5])
                sys.stdout.write(";%s" % perf_data[6])
                sys.stdout.write("|")
        sys.stdout.write(" %s" % self.summary)
        sys.stdout.write("\n")
        sys.stdout.flush()

    def batch_passive_out(self, hostname, metric_name, status, summary, details, perf_container=None):
        assert self.command_pipe

        if not self.dry_run and not os.path.exists(os.path.abspath(self.command_pipe)):
            log.error("Specified command file (%s) doesn't exist" % os.path.abspath(self.command_pipe))
            return

        timestamp = str(int(time.time()))
        host = hostname
        service = metric_name
        ret_code = status
        summary = "%s - %s" % (get_status(ret_code), summary)
        if perf_container:
            summary += " | "
            for perf_data in perf_container:
                summary += "%s=%s%s" % (perf_data[0], str(perf_data[1]), str(perf_data[2]))
                summary += ";%s" % perf_data[3]
                summary += ";%s" % perf_data[4]
                summary += ";%s" % perf_data[5]
                summary += ";%s" % perf_data[6]
                summary += " "
        summary += "\\n"
        details = summary + details.replace("\n", "\\n")
        details = details.encode('utf-8').replace(b'|', b'\u2758')
        log.debug(repr(details))

        if self.dry_run:
            p_msg = "[%s] PROCESS_SERVICE_CHECK_RESULT;%s;%s;%d;%s" % \
                    (timestamp, host, service, ret_code, details)
            log.debug(p_msg)
            return p_msg

        try:
            with open(os.path.abspath(self.command_pipe), "w") as cmd_pipe:
                cmd_pipe.write("[%s] PROCESS_SERVICE_CHECK_RESULT;%s;%s;%d;%s\n" %
                               (timestamp, host, service, ret_code, details))
                cmd_pipe.flush()
        except (IOError, OSError) as e:
            log.exception("Exception while writing to command pipe (%s)" % str(e))

    def plugin_passive_out(self):
        assert self.command_pipe

        if not self.dry_run and not os.path.exists(os.path.abspath(self.command_pipe)):
            log.error("Specified command file (%s) doesn't exist" % os.path.abspath(self.command_pipe))
            return

        if self.summary == "Plugin didn't set summary message":
            log.debug("Skipping submission of passive metric results (%s) as no summary was set" % self.metric_name)
            return

        timestamp = str(int(time.time()))
        host = self.hostname
        service = self.metric_name
        ret_code = self.status
        summary = "%s - %s" % (get_status(ret_code), self.summary)
        if self._perf_container:
            summary += " | "
            for perf_data in self._perf_container:
                summary += "%s=%s%s" % (perf_data[0], str(perf_data[1]), str(perf_data[2]))
                summary += ";%s" % perf_data[3]
                summary += ";%s" % perf_data[4]
                summary += ";%s" % perf_data[5]
                summary += ";%s" % perf_data[6]
                summary += " "
        summary += "\\n"
        details = summary + self._stdout.getvalue().replace("\n", "\\n")
        details = summary + details.replace("\n", "\\n")
        details = details.encode('utf-8').replace(b'|', b'\u2758')
        log.debug(repr(details))

        if self.dry_run:
            p_msg = "[%s] PROCESS_SERVICE_CHECK_RESULT;%s;%s;%d;%s" % \
                    (timestamp, host, service, ret_code, details)
            log.debug(p_msg)
            return p_msg

        try:
            with open(os.path.abspath(self.command_pipe), "w") as cmd_pipe:
                cmd_pipe.write("[%s] PROCESS_SERVICE_CHECK_RESULT;%s;%s;%d;%s\n" %
                               (timestamp, host, service, ret_code, details))
                cmd_pipe.flush()
        except (IOError, OSError) as e:
            log.exception("Exception while writing to command pipe (%s)" % str(e))

    def plugin_output(self, backend="nagios"):
        sys.stdout = sys_stdout
        sys.stderr = sys_stderr
        if backend == 'nagios':
            return self.plugin_nagios_out()
        elif backend == 'check_mk':
            return self.plugin_check_mk_out()
        elif backend == 'passive':
            return self.plugin_passive_out()
        else:
            log.error("unsupported backend %s" % backend)


class Plugin(object):
    def __init__(self, description=None, version="1.0"):
        self._parser = argparse.ArgumentParser(description=description)
        self.args = None
        self.sequence = list()
        self._version = version
        self._results = list()

        # setup core arguments
        self._parser.add_argument('--version', action='version', version='%(prog)s ' + self._version)
        self._parser.add_argument('-H', '--hostname', default="localhost",
                                  help='Host name, IP Address, or unix socket (must be an absolute path)')
        self._parser.add_argument('-w', '--warning', type=int, help='Offset to result in warning status')
        self._parser.add_argument('-c', '--critical', type=int, help='Offset to result in critical status')
        self._parser.add_argument('-d', '--debug', action='store_true', help='Specify debugging mode')
        self._parser.add_argument('-p', '--prefix', help='Text to prepend to ever metric name', default='')
        self._parser.add_argument('-s', '--suffix', help='Text to append to every metric name', default='')
        self._parser.add_argument('-t', '--timeout', help='Global timeout for plugin execution', type=int,
                                  default=3700)
        self._parser.add_argument('-C', '--command', default=NAGIOS_CMD,
                                  help='Nagios command pipe for submitting passive results')
        self._parser.add_argument('--dry-run', dest="dry_run", action="store_true",
                                  help="Dry run, will not execute commands and submit passive results")
        self._parser.add_argument('-o', '--output', default="nagios",
                                  help='Plugin output format; valid options are nagios, check_mk or passive '
                                       '(via command pipe); defaults to nagios)')

    def add_argument(self, *args, **kwargs):
        self._parser.add_argument(*args, **kwargs)

    def metric_results(self):
        return self._results

    def metric(self, seq=None, metric_name=None, passive=False):
        def decorator(f):
            if seq and seq > 0:
                self.sequence.insert(seq - 1, (f, metric_name if metric_name else f.__name__,
                                               passive))
            else:
                self.sequence.append((f, metric_name if metric_name else f.__name__,
                                      passive))
            log.debug("Registered callback: %s" % str(f.__name__))
            return f

        return decorator

    def _partial_order(self):
        partial_order = list()
        all_keys = set(key for key in self._dps_tree.keys())
        for k, v in self._dps_tree.items():
            v.discard(k)
        extra_items_in_deps = reduce(set.union, self._dps_tree.values()) - set(self._dps_tree.keys())
        for item in extra_items_in_deps:
            if item:
                self._dps_tree[item] = set()
        while True:
            ordered = set(item for item, dep in self._dps_tree.items() if not dep)
            if not ordered:
                break
            partial_order.extend(ordered)
            for item, dep in self._dps_tree.items():
                self._dps_tree_tmp = dict()
                if item not in ordered:
                    self._dps_tree_tmp[item] = (dep - ordered)
            self._dps_tree = self._dps_tree_tmp
        assert not self._dps_tree, "A cyclic dependency exists amongst %r" % self._dps_tree
        rest = list(all_keys - set(partial_order))
        partial_order.extend(rest)
        return partial_order

    def run(self):
        self.args = self._parser.parse_args()

        global sys_stdout, sys_stderr, plugin_stdout
        sys_stdout = sys.stdout
        sys_stderr = sys.stderr

        if self.args.debug:
            log.setLevel(logging.DEBUG)
            formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(module)s[%(process)d]: %(message)s',
                                          datefmt='%b %d %H:%M:%S')
            if sys.version_info[0] == 2 and sys.version_info[1] <= 6:
                fh = logging.StreamHandler(strm=sys_stdout)
            else:
                fh = logging.StreamHandler(stream=sys_stdout)
            fh.setFormatter(formatter)
            log.addHandler(fh)
        else:
            # prevent unintentional output from plugin
            sys.stdout = plugin_stdout = StringIO.StringIO()
            sys.stderr = plugin_stdout

        # run logic, metric call
        log.debug("Call sequence: %s " % str(self.sequence))
        for entry in self.sequence:
            metric_name = entry[1]
            if self.args.prefix:
                metric_name = self.args.prefix + '-' + metric_name
            if self.args.suffix:
                metric_name = metric_name + '-' + self.args.suffix
            passive = entry[2]  # output per metric
            if passive:
                output = "passive"
            else:
                output = self.args.output
            plugin_io = PluginIO(metric_name, self.args.hostname,
                                 command_pipe=self.args.command, dry_run=self.args.dry_run)
            plugin_function = entry[0]
            try:
                signal.signal(signal.SIGALRM, _handle_timeout)
                signal.alarm(self.args.timeout)
                log.debug("   Function call: %s" % str(plugin_function.__name__))
                plugin_function(self.args, plugin_io)
                plugin_io.plugin_output(backend=output)
            except Exception as e:
                plugin_io.status = nap.UNKNOWN
                plugin_io.summary = "Exception caught while executing plugin (%s)" % e
                plugin_io.plugin_output(backend=output)
                traceback.print_exc(file=sys.stdout)
            finally:
                self._results.append((plugin_function.__name__, plugin_io.status, plugin_io.summary, output))
                plugin_io.close()
                signal.alarm(0)

        # exit status is taken from first active metric executed
        ret_code = [e[1] for e in self._results if e[3] != "passive"][0]
        if not self.args.dry_run:
            os._exit(ret_code)
