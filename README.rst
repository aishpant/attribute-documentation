attribute documentation
-----------------------

`abi2doc` is a helper tool for generating and formatting sysfs attribute
documentation which is location under ``Documentation/ABI``\  in the kernel
source code.

From a `rough estimate`_, there are around 2000 attributes that are undocumented
in the kernel.

.. image:: https://plot.ly/~aishpant/1.png?share_key=8mG4JmyySLLYjbjTg7Uy62
   :target: https://plot.ly/~aishpant/1/?share_key=8mG4JmyySLLYjbjTg7Uy62
   :align: center
   :alt: sysfs line plot
   :width: 600px

The ABI documentation format looks like the following:

| What: (the full sysfs path of the attribute)
| Date: (date of creation)
| KernelVersion: (kernel version it first showed up in)
| Contact: (primary contact)
| Description: (long description on usage)

`abi2doc` can fill in the '`Date`' and the '`KernelVersion`' fields with high
accuracy. The '`Contact`' details is prompted for once, and the others '`What`'
and '`Description`' are prompted on every attribute.

It also tries to collect description from various sources-

-  From the commit message that introduced the attribute

-  From comments around the attribute show/store functions or the attribute
  declaring macro.

-  From the structure fields that map to the attribute.
   
   For eg. consider the attribute declaring macro `PORT_RO(dest_id)` and its
   show function `port_destid_show(...)`.

  .. code:: c

            static ssize_t
            port_destid_show(struct device *dev, struct device_attribute *attr,
                             char *buf)
            {
                    struct rio_mport *mport = to_rio_mport(dev);

                    if (mport)
                            return sprintf(buf, "0x%04x\n", mport->host_deviceid);
                    else
                            return -ENODEV;
            }



  The show functions typically contain a conversion to a driver private struct
  and then one or many fields from it are put in the buffer. 

  In the example above, the driver private structure is a struct of type
  `rio_mport` and the attribute `port_id` maps to the field `host_deviceid` in
  the structure.

  .. code:: c

      struct rio_mport {
            ...
            int host_deviceid;      /* Host device ID */
            struct rio_ops *ops;    /* low-level architecture-dependent routines */
            unsigned char id;       /* port ID, unique among all ports */
            ...
            };

  There's a comment against `host_deviceid` here and this can be extracted.

All sysfs attribute declaring macros are located in ``abi2doc/macros.txt``. Each
row of `macros.txt` contains an attribute declaring macro space separated by the
location of the attribute name in the macro - `DEVICE_ATTR 0`. This list is not
complete. Please send a pull request if you find any that are not in the list.

Usage
-----

Prerequisites:

-  Coccinelle - `install instructions`_
  spatch will need to be compiled with option `./configure --with-python=python3`
-  Python 3
-  Linux Kernel source code

`abi2doc` is available on `PYPI`_. Install with ``pip3``:

  ``pip3 install abi2doc``

The library is currently tested against Python versions `3.4+`.

.. code:: bash

    usage: abi2doc [-h] -f SOURCE_FILE -o OUTPUT_FILE

    Helper for documenting Linux Kernel sysfs attributes

    required arguments:
      -f SOURCE_FILE  linux source file to document
      -o OUTPUT_FILE  location of the generated sysfs ABI documentation

    optional arguments:
      -h, --help      show this help message and exit

Example usage:

.. code:: bash

    abi2doc -f drivers/video/backlight/lp855x_bl.c -o sysfs_doc.txt

The script will fill in the '`Date`' and the '`KernelVersion`' fields for found
attributes. The '`Contact`' details is prompted for once, and the others 'What'
and '`Description`' are prompted on every attribute. The entered description
will be followed by hints, as shown in a generated file below.

::

    What:       /sys/class/backlight/<backlight>/bled_mode
    Date:       Oct, 2012
    KernelVersion:  3.7
    Contact:    dri-devel@lists.freedesktop.org
    Description:
            (WO) Write to the backlight mapping mode. The backlight current
            can be mapped for either exponential (value "0") or linear
            mapping modes (default).
            --------------------------------
            %%%%% Hints below %%%%%
            bled_mode DEVICE_ATTR drivers/video/backlight/lm3639_bl.c 220
            --------------------------------
            %%%%% store fn comments %%%%%
            /* backlight mapping mode */
            --------------------------------
            %%%%% commit message %%%%%
            commit 0f59858d511960caefb42c4535dc73c2c5f3136c
            Author: G.Shark Jeong <gshark.jeong@gmail.com>
            Date:   Thu Oct 4 17:12:55 2012 -0700

                backlight: add new lm3639 backlight driver

                This driver is a general version for LM3639 backlgiht + flash driver chip
                of TI.

                LM3639:
                The LM3639 is a single chip LCD Display Backlight driver + white LED
                Camera driver.  Programming is done over an I2C compatible interface.
                www.ti.com

                [akpm@linux-foundation.org: code layout tweaks]
                Signed-off-by: G.Shark Jeong <gshark.jeong@gmail.com>
                Cc: Richard Purdie <rpurdie@rpsys.net>
                Cc: Daniel Jeong <daniel.jeong@ti.com>
                Cc: Randy Dunlap <rdunlap@xenotime.net>
                Signed-off-by: Andrew Morton <akpm@linux-foundation.org>
                Signed-off-by: Linus Torvalds <torvalds@linux-foundation.org>

Expected time for the scripts to run =

  `(num of attrs x avg 4 min per attr)/num of cores`.

Contributions
-------------

Contributions are welcome, whether it is in the form of code or documentation.
Please refer to the `issues`_ tab for places that need help.

.. _install instructions: https://github.com/coccinelle/coccinelle/
.. _PYPI: https://pypi.org/project/abi2doc/
.. _Coccinelle: http://coccinelle.lip6.fr/
.. _rough estimate: https://github.com/aishpant/documentation-scripts/blob/master/result/output.csv
.. _issues: https://github.com/aishpant/attribute-documentation/issues
