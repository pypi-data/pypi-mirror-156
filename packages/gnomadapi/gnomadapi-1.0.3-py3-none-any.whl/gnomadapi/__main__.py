from ensurepip import version
import os
from selenium import webdriver
import chromedriver_binary  # Adds chromedriver binary to path
from selenium.webdriver.chrome.options import Options
import time
from gnomadapi.GnomadAPI import GnomadAPI

#!/usr/bin/env python3
import argparse
import sys
#from importlib import resources
def main():
    parser = argparse.ArgumentParser(description='access to the gnomad database using selenium')

    #requiredNamed = subparsers.add_argument_group('required arguments')
    #parser.add_argument('-c','--chromosome', help='name of chromosome/contig', required=True)
    #parser.add_argument('-s','--start' ,help='start of region of interest', required=True)
    parser.add_argument('-g', '--gene',help='gene of interest', required=True)
    parser.add_argument('-v', '--version',help='gnomad Version', choices=['gnomad_sv_r2_1', 'gnomad_r3', 'gnomad_r2_1', 'exac'],
                        default='gnomad_r2_1' ,required=False)


    print(parser)
    args=parser.parse_args()
    c=GnomadAPI(gene=args.gene,version=args.version)

if __name__ == "__main__":
    main()

