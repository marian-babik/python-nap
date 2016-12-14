```
NAP - Python Library to write Nagios (Monitoring) Plugins with the following features:
- Supports writing both active and passive plugins
- Combination of active and mulitple passive plugins via sequences
- Passive plugin status via command file
- Output formats for nagios, passive (command pipe) or check_mk (local check)
- Wraps sys.stdout and sys.stderr to ensure correct output format with status 
and summary in the first line (regardless of exceptions, code execution flow, etc.)
- Supports performance data (also for passive metrics)
- Auto-defines basic command line arguments (e.g. -H, -v, -d, -w, -c, etc.)


Synopsis:
app = nap.core.Plugin()
app.add_argument("--test", help="define additional arguments (using argparse syntax")

@app.metric()
def test_metric(args, io):
    # code to take the measurment
    if args.test: # accessing arguments
        pass
    io.status = nap.OK  # setting exit status
    io.summary = "no issues"  # setting summary line
    
    print "detailed output"  # detailed output via print
    io.write("another detailed output")  # or directly to buffer

    io.add_perf_data("cpu", 0.24)
    io.add_perf_data("mem", 0.87, uom="%")
    
    # plugin status determined from io.status, return statement not needed

if __name__ == '__main__':
    app.run()

Sample run will output the following:
$ sample_plugin.py --help
usage: sample_plugin.py [-h] [--version] [-H HOSTNAME] [-w WARNING] [-c CRITICAL] [-d]
               [-p PREFIX] [-s SUFFIX] [-C COMMAND] [--dry-run] [-o OUTPUT]
               [--test TEST]

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -H HOSTNAME, --hostname HOSTNAME
                        Host name, IP Address, or unix socket (must be an
                        absolute path)
  -w WARNING, --warning WARNING
                        Offset to result in warning status
  -c CRITICAL, --critical CRITICAL
                        Offset to result in critical status
  -d, --debug           Specify debugging mode
  -p PREFIX, --prefix PREFIX
                        Text to prepend to ever metric name
  -s SUFFIX, --suffix SUFFIX
                        Text to append to every metric name
  -C COMMAND, --command COMMAND
                        Nagios command pipe for submitting passive results
  --dry-run             Dry run, will not execute commands and submit passive
                        results
  -o OUTPUT, --output OUTPUT
                        Plugin output format; valid options are nagios or
                        check_mk (defaults to nagios)
  --test TEST           additional argument


$ python sample_plugin.py
OK - no issues | cpu=0.24;;;; mem=0.87%;;;;
detailed output
another detailed output
$ python sample_plugin.py -o check_mk 
0 test_metric cpu=0.24;;;;|mem=0.87%;;;;| no issues

It's possible and easy to write passive plugins that report results via Nagios command pipe, e.g.
@app.metric(passive=True)
def test_metric(args, io):
    io.set_status(nap.OK, "summary line")
    
$ python sample_plugin.py --dry-run -d
Dec 14 11:58:57 DEBUG core[98727]: Call sequence: [(<function test_metric at 0x106a00050>, 'test_metric', True)] 
Dec 14 11:58:57 DEBUG core[98727]:    Function call: test_metric
Dec 14 11:58:57 INFO core[98727]: [1481713137] PROCESS_SERVICE_CHECK_RESULT;localhost;test_metric;0;no issues | cpu=0.24;;;; mem=0.87%;;;; \ndetailed output\nanother detailed output

In addition, complex active/passive plugin with a call sequence is also possible, e.g.
app = nap.core.Plugin()
app.add_argument("--test", help="define additional arguments (using argparse syntax")

@app.metric(seq=2, passive=True)
def test_m1(args, io):
    # test CPU
    io.set_status(nap.OK, "cpu ok")

@app.metric(seq=3, passive=True)
def test_m2(args, io):
    # test mem
    io.set_status(nap.CRITICAL, "out of memory")

@app.metric(seq=1, passive=False)
def test_all(args, io):
    # init
    app.container = list()

    def callback_function(results):  # results has io.status from all metrics
        if all(results) == 0:
            io.status = nap.OK
        if any(results) == 2:
            io.status = nap.CRITICAL
            
    app.register_callback(callback_function)

if __name__ == '__main__':
    app.run()


```