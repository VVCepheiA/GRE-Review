#! /usr/bin/env python
#-*- coding:utf-8 -*-

import argparse
import os
import time
from datetime import datetime
import pickle

DATA_DIR = "data/"
STATS_FILE = DATA_DIR + "checkpoint"


class Stats:
    def __init__(self):
        # the iteration reading from
        self.iteration = 0
        self.counter = 0
        self.remember_counter = 0
        self.cur_line = 0
        self.forget = set()


def get_data_file_name(stats):
    return DATA_DIR + str(stats.iteration) + ".tsv"


def save(stats_to_save):
    with open(STATS_FILE, 'wb') as file:
        pickle.dump(stats_to_save, file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--reset', help='Restart from base', action='store_true', required=False)
    args = parser.parse_args()

    if args.reset or not os.path.exists(STATS_FILE):
        stats = Stats()
        save(stats)

    with open(STATS_FILE, "rb") as pickle_file:
        stats = pickle.load(pickle_file)

    with open(get_data_file_name(stats), "r") as lines:
        try:
            # ignoring previous time...
            start_time = datetime.now()
            for i, line in enumerate(lines):
                if i < stats.cur_line:
                    continue
                stats.counter += 1
                word, translation = line.split("\t")
                print(word)
                time.sleep(0.3)
                print(translation)
                while True:
                    response = input().lower()
                    if response == 'y':
                        stats.remember_counter += 1
                        break
                    elif response == 'n':
                        stats.forget.add(i)
                        break
                    else:
                        print("Invalid response. Please enter Y or y for remember, N or n for forget.")
                if i % 100 == 9:
                    print("Remember %d/ %d words" % (stats.remember_counter, stats.counter))
                    delta = datetime.now() - start_time
                    print("Finished in %d minutes" % float(delta.total_seconds()/60))
                    stats.counter, stats.remember_counter = 0, 0
                    start_time = datetime.now()

            # Done reviewing one round, save to next iteration
            print("Saving Next Iteration")
            next_iteration = stats.iteration + 1

            with open(get_data_file_name(stats), "w+") as fout:
                for i, line in enumerate(lines):
                    if i in stats.forget:
                        fout.write(line[i])
            stats = Stats()
            stats.iteration = next_iteration
            save(stats)
        except KeyboardInterrupt:
            stats.cur_line = i
            # save progress
            save(stats)

