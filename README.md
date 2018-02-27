## attribute documentation

This is a helper tool for generating and formatting sysfs attribute
documentation which is location under `Documentation/ABI`in the kernel source.

From a rough estimate, there are around 2000 attributes that are undocumented in
the kernel.

<div>
    <a href="https://plot.ly/~aishpant/1/?share_key=8mG4JmyySLLYjbjTg7Uy62" target="_blank" title="sysfs line plot" style="display: block; text-align: center;"><img src="https://plot.ly/~aishpant/1.png?share_key=8mG4JmyySLLYjbjTg7Uy62" alt="sysfs line plot" style="max-width: 100%;width: 600px;"  width="600" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
</div>

The ABI documentation format looks like the following:

What:          (the full sysfs path of the attribute)  
Date:          (date of creation)  
KernelVersion: (kernel version it first showed up in)  
Contact:       (primary contact)  
Description:   (long description on usage)

The script can fill in the 'Date' and the 'KernelVersion' fields with high
accuracy. The 'Contact' details is prompted for once, and the others 'What' and
'Description' are prompted for every attribute.

It also tries to collect description from various sources-

* Commit message that introduced the attribute

* If suppose documentation is present somewhere, plain old grep for the
  attribute name in the Documentation folder. This is **disabled** right now
  because this sometimes outputs too many irrelevant results.

* Comments around show/store functions or the macro.

* From the structure fields that map to the attribute.

  The show functions usually look like this:
```c
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
```
  There is a conversion to some driver private struct and then one or many fields from
  it are put in the buffer.

  In the example above, it's a struct of type rio\_mport.
```c
  struct rio_mport {
        ...
        int host_deviceid;      /* Host device ID */
        struct rio_ops *ops;    /* low-level architecture-dependent routines */
        unsigned char id;       /* port ID, unique among all ports */
        ...
        };
```
  There's a comment against host\_deviceid here and this can be extracted.

All sysfs attribute declaring macros are located in `macros.txt`. Each row of
`macros.txt` contains an attribute declaring macro space separated by the
location of the attribute name in the macro - DEVICE\_ATTR 0. This list is not
complete. Please send a pull request if you find any that are not in the list.


## Usage

Prerequisites:
- Coccinelle - [install instructions](http://coccinelle.lip6.fr/download.php)
- Python 3
- Linux Kernel source code

First, you need to clone the project. The `make` utility needs two options- path
to the kernel source files or directory which needs documentation, and the path
to the kernel source.

```bash
make doc FILE=$(source file or directory) KERNEL_PATH=$(path to kernel source)
make clean # clean temporary & generated files
```
Example usage:

```bash
make doc FILE=~/projects/linux/drivers/video/backlight/lp855x_bl.c KERNEL_PATH=~/projects/linux
```

The script will fill in the 'Date' and the 'KernelVersion' fields for found
attributes. The 'Contact' details is prompted for once, and the others 'What' and
'Description' are prompted for every attribute.

While `make doc` runs, it will create a `description.txt`file containing possible
descriptions for the attributes. Please refer to it while filling in the
documentation. The formatted documentation is appended to a file named
`sysfs_doc`.


## Contributions

Thank you for reading up till here. Contributions are welcome, whether it is in
the form of code or documentation. This projects consists of scripts written in
Python 3 and [Coccinelle](http://coccinelle.lip6.fr/).

Some top of the mind tasks are:

- [ ] spatch runs assuming 4 cores. This should be corrected to match the
  developer's machine
- [ ] support for verbose & quiet mode. Some print statements are for debugging
  purpose and they should be printed in verbose mode only.
- [ ] utilise all cores. The `git log -L` command in doc.py takes a _very_ long
  time to run. The script would be much faster if it runs in parallel.
- [ ] code cleanup. Some for-loops can be replaced by list comprehensions.
