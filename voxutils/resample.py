import pygst
pygst.require("0.10")
import gst
import sys, os


def resample_pipeline(filename, outfilename, rate):
    uri = 'file://' + os.path.abspath(filename)
    s = ("uridecodebin uri=%s "
         "! audioconvert "
         "! audio/x-raw-int,channels=1,width=16,depth=16 "
         "! audioresample "
         "! audio/x-raw-int, rate=%s "
         "! wavenc "
         "! filesink location=%s"
         % (uri, rate, outfilename))
    print s
    pipeline = gst.parse_launch(s)
    return pipeline

def convert_one(filename, outfilename=None, rate=16000):
    if outfilename is None:
        outfilename = '%s-%s.wav' % (filename.rsplit('.', 1)[0], rate)
    pipeline = resample_pipeline(filename, outfilename, rate)
    pipeline.set_state(gst.STATE_PLAYING)
