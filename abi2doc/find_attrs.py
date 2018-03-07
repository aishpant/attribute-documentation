import os, glob
import multiprocessing

def get_macros():
    fname = os.path.join(os.path.dirname(__file__), 'macros.txt')
    with open(fname, "r") as filename:
       # filter commented lines
       return [line for line in filename.readlines() if not line.startswith('#')]

def write_cocci_output(filename, dir_file):
    #print ('Processing file ' + str(filename))
    # run coccinelle on drivers
    num_of_cores = str(multiprocessing.cpu_count())
    os.system('spatch -j ' + num_of_cores + ' --very-quiet --sp-file ' + str(filename) + ' --dir ' + dir_file + '>' + '/tmp/out.' + str(os.path.basename(filename)))
    #print ('########################################################')

def generate_scripts(dir_file):
    # get all attribute declarers with pos info
    lines = get_macros()
    lines = [x.strip() for x in lines]

    for idx, line in enumerate(lines):
        macro, attr_pos = line.split()
        with open('/tmp/batch_find_' + str(idx) + '.cocci', 'w') as fil:
            fil.write("@initialize:python@\n@@\ns = set()\n\n")
            fil.write("@r@\nexpression list[" + attr_pos + "]" +  "es;\nidentifier attr, i;\ndeclarer mac = " + macro + ";\nposition p;\n@@\n")
            fil.write("mac(es, attr@i@p, ...);\n\n")
            fil.write("@script:python depends on r@\nattr<<r.i;\nmac<<r.mac;\np<<r.p;\n@@\n");
            fil.write("s.add((mac, attr, p[0].file, p[0].line))\nprint (s)\n")
            fil.close()

# get all the generated cocci scripts
    cocci_scripts = glob.glob("/tmp/batch_find_*")

    for script in cocci_scripts:
        write_cocci_output(script, dir_file)

'''
if __name__ == "__main__":
    import sys
    # argv[1] is the path to the kernel source file or directory
    generate_scripts(sys.argv[1])
'''
