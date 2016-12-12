import unittest
import logging
import sys

import nap.core

log = logging.getLogger("wnfm")
log.setLevel(logging.INFO)
formatter = logging.Formatter(fmt='%(message)s')
if sys.version_info[1] <= 6:
    fh = logging.StreamHandler(strm=sys.stdout)
else:
    fh = logging.StreamHandler(stream=sys.stdout)
fh.setFormatter(formatter)
log.addHandler(fh)


class NAPTests(unittest.TestCase):
    def test_basics(self):
        app = nap.core.Plugin()
        app.add_argument("--test", help="additional argument", default="yes")

        @app.metric()
        def test_metric(args, io):
            app.args.dry_run = True

            io.status = 0
            io.summary = "OK - no issues"
            print "detailed output"
            print "print statement"
            print "another print statement"
            print args
            io.status = 1
            io.add_perf_data("cpu", 0.24)
            io.add_perf_data("mem", 0.87, uom="%")

            self.assertEquals(args.test, "yes")
            self.assertTrue("detailed output" in io.getvalue())
            self.assertEqual(io.status, 1)

        @app.metric()
        def test_metric2(args, io):
            io.status = 0
            io.summary = "OK - no issues"
            print "detailed output"
            print "print statement"
            print "another print statement"
            print args
            io.status = 1
            io.add_perf_data("cpu", 0.24)
            io.add_perf_data("mem", 0.87, uom="%")

            self.assertTrue("detailed output" in io.getvalue())
            self.assertEqual(io.status, 1)

        app.run()

    def test_sequence(self):
        app = nap.core.Plugin()
        call_seq = ['test_metric3', 'test_metric', 'test_metric2']

        @app.metric()
        def test_metric(args, io):
            io.status = 0
            io.summary = "OK - no issues"
            print "detailed output"
            call_seq.remove('test_metric')
            self.assertEqual(call_seq, ["test_metric2"])


        @app.metric()
        def test_metric2(args, io):
            io.status = 0
            io.summary = "OK - no issues"
            print "detailed output"
            call_seq.remove('test_metric')
            self.assertFalse(call_seq)

        @app.metric(seq=1)
        def test_metric3(args, io):
            app.args.dry_run = True

            io.status = 0
            io.summary = "OK - no issues"
            print "detailed output"
            call_seq.remove('test_metric3')
            self.assertEqual(call_seq, ["test_metric", "test_metric2"])


if __name__ == '__main__':
    unittest.main()
