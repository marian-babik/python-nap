Python Library to write Nagios (Monitoring) Plugins (NAP) with following features:
- Supports writing both active and passive checks
- Combination of active and mulitple passive checks via sequences
- Passive check status sent via command file
- Output formats for nagios, passive (command pipe) or check_mk (local check)
- Wraps sys.stdout and sys.stderr to ensure correct output format with status 
and summary in the first line (regardless of exceptions, code execution flow, etc.)
- Supports performance data (also for passive metrics)
- Auto-defines basic command line arguments (e.g. -H, -v, -d, -w, -c, etc.)


Synopsis:
```
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
```
Writing passive plugins that report results via Nagios command pipe is easy, e.g.
```
@app.metric(passive=True)
def test_metric(args, io):
    io.set_status(nap.OK, "summary line")
    
$ python sample_plugin.py --dry-run -d
Dec 14 11:58:57 DEBUG core[98727]: Call sequence: [(<function test_metric at 0x106a00050>, 'test_metric', True)] 
Dec 14 11:58:57 DEBUG core[98727]:    Function call: test_metric
Dec 14 11:58:57 INFO core[98727]: [1481713137] PROCESS_SERVICE_CHECK_RESULT;localhost;test_metric;0;no issues | cpu=0.24;;;; mem=0.87%;;;; 
```
Complex plugin with a sequence of active and multiple passive metrics is also possible, e.g.
```
app = nap.core.Plugin()
app.add_argument("--test", help="define additional arguments (using argparse syntax")

@app.metric(seq=2, passive=True)
def test_m1(args, io):
    # test CPU
    io.set_status(nap.OK, "cpu ok")

@app.metric(seq=1, passive=True)
def test_m2(args, io):
    # test mem
    io.set_status(nap.CRITICAL, "out of memory")

@app.metric(seq=3, passive=False)
def test_all(args, io):
    print "active probe that aggregates m1 and m2"

    results = app.metric_results()

    statuses = [e[1] for e in results]
    print statuses
    if all(st == 0 for st in statuses):
        io.set_status(nap.OK, "All fine")
    if 2 in statuses:
        io.set_status(nap.CRITICAL, "Not quite")
        
if __name__ == '__main__':
    app.run()

$ python sample_plugin.py --dry-run -d
Dec 16 09:50:08 DEBUG core[16183]: Call sequence: [(<function test_m2 at 0x10718c140>, 'test_m2', True), 
                                                   (<function test_m1 at 0x10718c1b8>, 'test_m1', True), 
                                                   (<function test_all at 0x10718c230>, 'test_all', False)] 
Dec 16 09:50:08 DEBUG core[16183]:    Function call: test_m2
Dec 16 09:50:08 INFO core[16183]: [1481878208] PROCESS_SERVICE_CHECK_RESULT;localhost;test_m2;2;general failure\noutput from m2\n
Dec 16 09:50:08 DEBUG core[16183]:    Function call: test_m1
Dec 16 09:50:08 INFO core[16183]: [1481878208] PROCESS_SERVICE_CHECK_RESULT;localhost;test_m1;0;no issues | cpu=0.24;;;; mem=0.87%;;;; \noutput from m1\n
Dec 16 09:50:08 DEBUG core[16183]:    Function call: test_all
CRITICAL - Not quite
output from all


```