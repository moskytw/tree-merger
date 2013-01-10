#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from os import path
from pipes import quote

class Tree(dict):

    #{
    #   'origin_path': {
    #       'hash_A': ['source_path_A_1', 'source_path_A_2', ...],
    #       'hash_B': ['source_path_B_1', ...],
    #       ...
    #   }
    #   ...
    #}

    def __init__(self, root=''):
        self.root = root

    def add_hash(self, origin_path, hash_, source_prefix=None):
        # just add a hash record into tree
        possibles = self.setdefault(origin_path, {})
        sources = possibles.setdefault(hash_, [])

        if source_prefix:
            source_path = path.normpath(path.join(source_prefix, origin_path))
        else:
            # NOTE: `source_prefix` is optional,
            #       but you may encounter some problems if you don't give it
            # TODO: find the possible problems are the above said, and fix them
            source_path = origin_path

        sources.append(source_path)
    def parse_hash_lines(self, lines, source_prefix=None, drop_pattern=None):
        # add lines with source prefix
        for line in lines:
            hash_, __, origin_path = line.strip().partition('  ')
            # drop the matched path
            if drop_pattern and drop_pattern.search(origin_path):
                continue
            self.add_hash(origin_path, hash_, source_prefix)

    def parse_hash_files(self, relpaths, drop_pattern=None):
        # use the following command in different source directories
        #
        #   $ find . -exec md5sum {} + > md5sum.list
        #
        # and use this method to add the lists
        #
        #   tree.parse_hash_files(['a/md5sum.list', 'b/md5sum.list'])
        #
        for relpath in relpaths:
            file_path = path.join(self.root, relpath)
            with open(file_path) as f:
                # use dirname (path) as the prefix of source path
                self.parse_hash_lines(f, path.dirname(relpath), drop_pattern)

    def gen_merging_script(self, rebuild_prefix='merged'):
        # generate a merging script

        made_dir_paths = set()
        # sort by number of possibles (desc)
        # , so the conflict cases will at the top of this script
        for origin_path in sorted(self.keys(), key=lambda origin_path: len(self[origin_path]), reverse=True):

            # the new location of this file
            rebuild_path = path.normpath(path.join(self.root, rebuild_prefix, origin_path))

            # ignore if this file exists
            if path.exists(rebuild_path):
                print '# ingore %s, file exists' % rebuild_path
                continue

            # create the directory if we didn't create
            dir_path = path.dirname(rebuild_path)
            if dir_path not in made_dir_paths:
                print "mkdir -p %s" % quote(dir_path)
                print
                made_dir_paths.add(dir_path)

            # the possibles of this file
            possibles = self[origin_path]
            if len(possibles) == 1:
                # simplest case, only found an unique hash of this file
                sources = possibles.values()[0][:]
                # pick a source randomly
                print "cp --preserve=all %s %s" % (quote(sources.pop(0)), quote(rebuild_path))
                if len(sources):
                    print '# other sources which have same hash'
                    print '# --- start ---'
                    for source in sources:
                        print "#cp --preserve=all %s %s" % (quote(source), quote(rebuild_path))
                    print '# --- end ---'

            else:
                # a location has two or more hashes, let user determine which source is correct
                print '# CONFLICT!'
                print '# --- start ---'
                for sources in possibles.values():
                    print "#cp --preserve=all %s %s" % (quote(sources[0]), quote(rebuild_path))
                print '# --- end ---'

            print

if __name__ == '__main__':

    # TEST CASE

    #tree = Tree('/home/mosky/tmp/')
    #tree.parse_hash_files(['a/md5sum.a', 'b/md5sum.b'])

    #from pprint import pprint
    #pprint(tree)

    #tree.gen_merging_script('/home/mosky/merged')

    # REAL CASE

    tree = Tree('/media/mosky/Acer/Users/Mosky/Documents/')
    tree.parse_hash_files([
        '/media/mosky/Acer/Users/Mosky/Documents/md5sum.130110',
        '/media/mosky/MOSKY-FLASH/md5sum.130110',
        '/media/mosky/QUICK/md5sum.130110',
    ])

    #from pprint import pprint
    #pprint(tree)

    tree.gen_merging_script()
