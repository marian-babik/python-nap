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
    io.status = 0  # setting exit status
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
                        Plugin output format; valid options are nagios,
                        check_mk or passive (via command pipe); defaults to
                        nagios)
  --test TEST           additional argument


$ sample_plugin.py -H localhost
OK - no issues | cpu=0.24;;;; mem=0.87%;;;;
detailed output
another detailed output

```