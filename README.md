# Tree Merger

I will backup files in my desktop, laptop and server, but I always forgot to sync them.

It is a terrible thing to merge the different versions of my file tree which has more than ten thousands of files, so I wrote this script for helping me to merge them.

## Example

First, we simulate two different versions of the file tree:

    $ mkdir -p tmp/a tmp/b
    $ cd tmp/a
    $ echo 1 > x; echo 2 > y; echo 3 > z
    $ cp x y ../b
    $ cd ..
    $ echo changed > b/y

Now, we have some files in `a` and `b`:

1. `x` is same in both `a` and `b`
2. `y` has two different version
3. `z` is only in the `a`

Before using the Tree Merger, we have to calculate the hashes of the files. For an example, you can use the following command under each `a` and `b` to get the hash list:

    $ find . -exec md5sum {} + > md5sum.list

Then, enter the Python shell (under `tmp`):

    from tree import Tree

    tree = Tree()

    tree.parse_hash_files([
        'a/md5sum.list',
        'b/md5sum.list',
    ])

    tree.gen_merging_script()

You will get a merging script:

    mkdir -p merged

    # CONFLICT!
    # --- start ---
    #cp --preserve=all a/y merged/y
    #cp --preserve=all b/y merged/y
    # --- end ---

    cp --preserve=all a/x merged/x
    # other sources which have same hash
    # --- start ---
    #cp --preserve=all b/x merged/x
    # --- end ---

    cp --preserve=all a/z merged/z

Edit the part of CONFLICT, and execute this script to get the merged file tree.

Hope it would help you!




    
