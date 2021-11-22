# python-gdb-scripts
helper for gdb in python

Warnings, those scripts are made for Risc-V platforms

# Make sure your gdb is compatible
Make sure the gdb version your using have been compiled
with python support.
```
$gdb --configuration
This GDB was configured as follows:
   configure --host=x86_64-linux-gnu --target=x86_64-linux-gnu
             --with-auto-load-dir=$debugdir:$datadir/auto-load
             --with-auto-load-safe-path=$debugdir:$datadir/auto-load
             --with-expat
             --with-gdb-datadir=/usr/share/gdb (relocatable)
             --with-jit-reader-dir=/usr/lib/gdb (relocatable)
             --without-libunwind-ia64
             --with-lzma
             --with-babeltrace
             --with-intel-pt
             --with-mpfr
             --with-xxhash
             --with-python=/usr (relocatable)
             --with-python-libdir=/usr/lib (relocatable)
             --with-debuginfod
             --without-guile
             --enable-source-highlight
             --with-separate-debug-dir=/usr/lib/debug (relocatable)
             --with-system-gdbinit=/etc/gdb/gdbinit
             --with-system-gdbinit-dir=/etc/gdb/gdbinit.d

("Relocatable" means the directory can be moved with the GDB installation
tree, and GDB will still find it.)
```
You can notice the line `--with-python-libdir=/usr/lib (relocatable)`

# How to use an helper?

After cloning the repo.

## In gdb

- source the file and use commands
```
source <project path>/python-gdb-scripts/riscv_tools.py
sv39translate $mepc
```

# Commands

- **sv39translate**
`sv39translate <address or convenience variable>`
    ex :
    ```
    (gdb) sv39translate 0xffffffe0004798fa
    access rights: r:1 w:0 x:1
    pAddr: 0x806798fa
    (gdb) sv39translate $mepc
    access rights: r:1 w:0 x:1
    pAddr: 0x806798fa
    ```

- **sv48translate**
`sv48translate <address or convenience variable>`
