import sys
import os
from xlcrf.CRF import CRF
# from xlcrf.argparser import argparser

def usage():
    print("""Usage:   
       xlcrf structure_file.xlsx   
""")

def main():
    if len(sys.argv) != 2:
        usage()
    else:
        f = sys.argv[1]
        outdir = "."
        outfile = os.path.basename(os.path.splitext(f)[0] + "_CRF.xlsx")
        outpath = os.path.join(outdir, outfile)
        crf = CRF()
        crf.read_structure(f)
        crf.create(outpath)
        return(0)
