from distutils.version import StrictVersion
from multiprocessing import Pool
from tempfile import mkstemp
from pathlib import Path
from os import path, fdopen, remove
import subprocess
import argparse
import textwrap
import datetime
import re
from abi2doc.join_attrs import print_attrs

# clean-up all the generated temporary files
def remove_temp_files():
    for p in Path("/tmp/").glob("*.cocci"):
        p.unlink()

def run(command):
    output = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
             shell=True).communicate()[0].decode('utf-8').strip()
    return output

def add_description(attr, lines, comment=''):
    desc = attr_description.get(attr, '')
    desc += '--------------------------------\n'
    if comment:
        desc += (comment + '\n')
    desc += lines
    desc += '\n'
    attr_description[attr] = desc

# grep for comments around (line - 10) & line
def add_comments(attr, filename, line_num, comment=''):
    lower, upper = str(int(line_num) - int(10)), line_num
    match_comments = 'sed -n \'/^\/\*/p; /^ \*/p;/\/\/.*/p\''
    command = 'sed -n ' + lower + ',' + upper + 'p ' + filename + ' | ' + match_comments
    out = run(command)
    if out:
        add_description(attr, out, comment)

# generate cocci file by replacing a pattern by a substring
def replace_cocci(file_path, substr, pattern):
    fh, abs_path = mkstemp(suffix='.cocci')
    with fdopen(fh, 'w') as new_file:
        with open (file_path, 'r') as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, substr))
    return abs_path

# get show/store func lines from cocci output
def get_func_lines(file_path, linux_source_file):
    line_num = {}
    command = 'spatch -j 4 --very-quiet --sp-file ' + file_path  + ' --dir ' + linux_source_file
    out = run(command)
    if out:
        lines = out.split('\n')
        line_num['show'] = [' '.join(line.split()[1:]) for line in lines if line.startswith('show')]
        line_num['store'] = [line.split()[1] for line in lines if line.startswith('store')]
    return line_num

# get struct definition which is used in show fn
def add_struct_comments(attr, show_fn, filename, comment=''):
    cocci_script = path.join(path.dirname(__file__), 'cocci/get_show_struct.cocci')
    # print ('show_fn ' + show_fn)
    temp_show_script = replace_cocci(cocci_script, show_fn, 'show_fn')

    command = 'spatch -j 4 --very-quiet --sp-file ' + temp_show_script + ' --dir ' + filename
    out = run(command)
    if out:
        add_description(attr, out, comment)
        # get struct definition if show struct exists
        # another cocci script - match_struct.cocci / replace struct_type
        struct_type = [l.split(' ')[1] for l in out.splitlines() if l.startswith('struct_type')]
        if (len(struct_type) > 0):
            cocci_script = path.join(path.dirname(__file__), 'cocci/match_struct.cocci')
            temp_struct_script = replace_cocci(cocci_script, struct_type[0], 'struct_type')
            command = 'spatch -j 4 --very-quiet --include-headers --sp-file ' + temp_struct_script + ' --dir .'
            out = run(command)
            if out:
                add_description(attr, out)
            remove(temp_struct_script)
    remove(temp_show_script)

def print_formatted(fname, what, commit_date, kernel_version, contacts, description):
    print ('What:\t\t' + what, file = fname)
    print ('Date:\t\t' + commit_date, file = fname)
    print ('KernelVersion:\t' + kernel_version, file = fname)
    print ('Contact:\t' + contacts, file = fname)
    print ('Description:' + description, file = fname)
    print ('\n', file = fname)

def get_first_commit(attr, filename, line_num):
    # get the first commit that introduced the line
    command = 'git log --pretty=format:\'%h %cd\' --date=format:\'%m/%Y\' -L ' + line_num + ',' + line_num + ':' + filename + ' --reverse'
    output = run(command)
    if output:
        # get the oldest commit
        res = output.split('\n')[0]
        commit_hash, date = res.split()
        return (attr, commit_hash, date)

def run_parallel(attrs_info):
    pool = Pool()
    tasks = [(attr.split()[0], attr.split()[2], attr.split()[3]) for attr in attrs_info]
    results = [pool.apply_async(get_first_commit, t) for t in tasks]
    attr_commit = {}
    for result in results:
        (attr, commit_hash, date) = result.get()
        attr_commit[attr] = [commit_hash, date]
    return attr_commit

# Global variables
attr_description = {}

def document():
    parser = argparse.ArgumentParser(description='Helper for documenting Linux Kernel sysfs attributes')
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument('-f', required=True, type=str, dest='source_file',
                        help='linux source file to document')
    required.add_argument('-o', required=True, type=str, dest='output_file',
                        help='location of the generated sysfs ABI documentation')
    parser._action_groups.append(optional)

    args = parser.parse_args()
    driver_dir = args.source_file
    doc_file = args.output_file
    doc_list = []

    # make sure everything is clean before starting up
    remove_temp_files()

    attrs_info = print_attrs(driver_dir)
    attrs_info = list(filter(None, attrs_info.split('\n')))
    attrs = [line.split() for line in attrs_info]
    print ("########## Starting processing ##########")

    f = open(doc_file, 'w')

    attr_commit = run_parallel(attrs_info)

    for attr_info in attrs_info:
        attr, mac, filename, macro_line_num = attr_info.split()
        add_description(attr, attr_info, "%%%%% Hints below %%%%%")
        print (attr_info)

        # run a plain old grep for occurences in Documenation/ folder
        #command = 'git grep -A1 -B1 \'' + attr + '\' Documentation/'
        #grep_attr = run(command)
        #if grep_attr:
        #    add_description(attr, grep_attr)

        # get comments around the declaring macro, if present
        add_comments(attr, filename, macro_line_num, '%%%%% macro comments %%%%%');

        show_fn = ''
        standard_macro = False
        # get comments from show & store fns of standard macros, if present
        if (re.match('DEVICE_ATTR(?:_RO|_RW|_WO)?$', mac)):
           # write a cocci script to get line numbers of show/store if they exist
           standard_macro = True
           cocci_script = path.join(path.dirname(__file__), 'cocci/show_store.cocci')
           temp_cocci_script = replace_cocci(cocci_script, attr, 'attrname')
           func_lines = get_func_lines(temp_cocci_script, filename)
           remove(temp_cocci_script)
           if 'show' in func_lines and len(func_lines['show']) > 0:
                show_fn, show_line_num = func_lines['show'][0].split()
                add_comments(attr, filename, show_line_num, '%%%%% show fn comments %%%%%')
           if 'store' in func_lines and len(func_lines['store']) > 0:
                store_line_num = func_lines['store'][0]
                add_comments(attr, filename, store_line_num, '%%%%% store fn comments %%%%%')

        # write another script that extracts comments from struct fields
        # of a standard show fn
        if show_fn:
            # print ('standard macro')
            add_struct_comments(attr, show_fn, filename, '%%%%% struct comments %%%%%')
        elif not standard_macro:
            # do a brute force check for show/store func using all arguments
            command = 'sed \'' + macro_line_num + 'q;d\' ' + filename
            out = run(command)
            print (out)
            # no need for if check, we know it exists
            out =  out.strip(' );\t\n\r').split('(')[1]
            macro_arguments = out.split(',')
            # strip extra spaces
            macro_arguments = [arg.strip() for arg in macro_arguments]
            [add_struct_comments(attr, arg, filename) for arg in macro_arguments]


        # get the first commit that introduced the line
        # TODO: run git log -L in parallel
        commit_hash, date = attr_commit[attr]

        # get the commit message that added the attribute
        command = 'git log -n 1 --pretty=medium ' + commit_hash
        output = run(command)

        if output:
            add_description(attr, output, '%%%%% commit message %%%%%')

        command = 'git tag --contains=' + commit_hash
        output = run(command)
        tags = output.split('\n')
        tags = [tag[1:] for tag in tags if tag.startswith('v') and 'rc' not in tag]
        # this fails (!!) when the commit is not in a stable kernel version
        kernel_version = sorted(tags,  key=StrictVersion)[0]
        doc_list.append([attr, date, kernel_version])
        print (attr, date, kernel_version)

    doc_list = sorted(doc_list, key=lambda x: datetime.datetime.strptime(x[1], '%m/%Y'))
    print ("#################################")

    contacts = input("Contact: ")
    contacts = contacts.split(',')
    contacts = [contact.strip() for contact in contacts]
    contacts = (',\n\t\t').join(contacts)

    for doc in doc_list:
        attr, commit_date, kernel_version = doc[0], doc[1], doc[2]
        commit_date = (datetime.datetime.strptime(commit_date, "%m/%Y")).strftime("%b, %Y") # Jan, 2018
        print ('Fill in documentation for: ' + attr, commit_date, kernel_version)
        what = input("What: ")
        lines = ''
        while True:
            line = input('Description: ')
            if line:
                if not line[-1].isspace():
                    line += ' ';
                lines += line
            else:
                break
        lines = textwrap.wrap(lines, width=64)
        lines = [line.strip() for line in lines]
        description = '\n\t\t'.join(lines)
        description = '\n\t\t' + description
        description += '\n\t\t'

        hints = attr_description[attr]
        hints = hints.split('\n')
        description += '\n\t\t'.join(hints)

        print_formatted(f, what, commit_date, kernel_version, contacts,
                description)
    f.close()

    # clean-up temp cocci files
    remove_temp_files()
