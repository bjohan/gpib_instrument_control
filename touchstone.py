#!/usr/bin/python3
import numpy as np
import skrf as rf
import os
import glob
from matplotlib import pyplot as plt

if __name__ == "__main__":
    import argparse
    parser=argparse.ArgumentParser(description='Perform operations on touchstone files')
    parser.add_argument('-p', '--plot', help="List of files to plot. If argument is given without arguments then result of operation will be plotted", nargs="*")
    parser.add_argument('-s', '--s-matrix-elements', help="list of s matrix elements to plot, 11, 12, 21 or 22", nargs="*")
    parser.add_argument('-wtf', '--write_touchstone_file', help="Write result of operation to tuchstone file", nargs=1)

    og = parser.add_argument_group("Operations")
    ops=og.add_mutually_exclusive_group();
    ops.add_argument('-c', '--cascade', help = "List of s2p files to be cascaded", nargs="*");
    ops.add_argument('-d', '--deembed', help = "De embed first s2p from second", nargs=2);
    args = parser.parse_args()

    
    opOut = None

    if args.cascade:
        toCascade=[]
        for file in args.cascade:
            toCascade.append(rf.Network(file))
        opOut=rf.cascade_list(toCascade)

    if args.deembed:
        a = rf.Network(args.deembed[0])
        b = rf.Network(args.deembed[1])
        opOut = rf.de_embed(a,b) 

    ntwks = []
    if opOut is not None:
        ntwks.append(opOut)

    for file in args.plot:
        ntwks.append(rf.Network(file))

    if args.plot is not None:
        for n in ntwks:
            if args.s_matrix_elements:
                if "11" in args.s_matrix_elements:
                    n.plot_s_db(m=0, n=0)
                if "12" in args.s_matrix_elements:
                    n.plot_s_db(m=0, n=1)
                if "21" in args.s_matrix_elements:
                    n.plot_s_db(m=1, n=0)
                if "22" in args.s_matrix_elements:
                    n.plot_s_db(m=1, n=1)
            else:
                n.plot_s_db()
        plt.grid(True)
        plt.show()
        
    if args.write_touchstone_file:
        opOut.write_touchstone(args.write_touchstone_file[0])

