import sys, os
import subprocess

def convert_one(filename, outfilename, rate=16000):
    subprocess.call([
        "sox",
        filename,
        "-b", "16", "-r", str(rate), "-c", "1",
        outfilename
        ])

