from json import loads
from sys import argv
from sys import exit
from getopt import getopt
from getopt import GetoptError


version = 'version 0.0.1a'
DEBUG    = False
HELP     = False
RAW_MODE = False
filename = ''
statuses  = {}
lengths   = {}
words_    = {}
lines     = {}
durations = {}
status_filters = []
sortByField0 = lambda x:int(x[0])
sortByField1 = lambda x:int(x[1])
sortBy = sortByField0


def handle_result(result):
    global statuses
    global lengths
    global words_
    global fuzzes
    global lines
    global duration
    status = result['status']
    length = result['length']
    words  = result['words']
    lines_  = result['lines']
    duration = result['duration']
    if status not in status_filters:
        statuses[status] = statuses.get(status, 0) + 1
        lengths[length]  =  lengths.get(length, 0) + 1
        words_[words]    =   words_.get(words, 0)  + 1
        lines[lines_]    =    lines.get(lines_, 0) + 1
        # special handling for duration
        if RAW_MODE:
            durations[duration] = durations.get(duration, 0) + 1
        else:
            d_ms = duration // 1000000
            durations[d_ms] = durations.get(d_ms, 0) + 1


def print_dict(d, keyFun):
    d_sorted = sorted( d.items(), key=keyFun)
    d_sorted.reverse()
    vals = []
    for k,v in d_sorted:
        vals.append(f"{k:10}{v:10}")
    vals_ = "\n".join(vals)
    print( vals_ )


def printd(d, flag):
    v2 = ""
    if len(d.keys()):
        d_sorted = sorted( d.items(), key=lambda kv: int(kv[1]))
        d_sorted.reverse()
        vals = []
        for k,v in d_sorted:
            if v > 1:
                vals.append(f'{k}')
        if len(vals):
            vals.sort(key=lambda x:int(x))
            vals_ = ",".join(vals)
            v2 = f'{flag} {vals_}'
    return v2


def print_debug_dict(t, d, sortBy):
    if len(d.keys()):
        print(t)
        print_dict(d, sortBy)
        print('-'*20)


def print_debug(sortBy):
    print('-'*20)
    print_debug_dict('status code', statuses, sortBy)
    print_debug_dict('content length', lengths, sortBy)
    print_debug_dict('word count', words_, sortBy)
    print_debug_dict('line count', lines, sortBy)
    print_debug_dict('durations', durations, sortBy)


def get_options(argv):
    try:
        opts, args = getopt(argv[1:],'hvi:psc:', ['help', 'verbose', 'input=', 'sort-by-param', 'sort-by-value', 'code='])
    except getopt.GetoptError as err:
        print(err)
        exit(-1)
    return opts, args


def handle_options(opts):
    global DEBUG
    global HELP
    global status_filters
    global filename
    global sortBy
    for o,a in opts:
        if o == '-h':
            HELP = True
        elif o == '-v':
            DEBUG = True
        elif o in ('-i', '--input'):
            filename = a
        elif o in ('-p', '--sort-by-param'):
            sortBy = sortByField0
        elif o in ('-s', '--sort-by-value'):
            sortBy = sortByField1
        elif o in ('-c', '--code'):
            status_filters = [int(x) for x in a.split(',')]
        else:
            assert(False, 'Unhandled option')


def print_usage():
    print('ffuflags by darkmage')
    print(f'{version}')
    print()
    print('python3 -m ffuflags -i <input_ffuf_file.json>')
    print('\t[-v/--verbose] [-p/--sort-by-param]')
    print('\t[-s/--sort-by-value] [-c/--code]')
    print()
    print()
    print()
    print('example usage:')
    print()
    print('python3 -m ffuflags -i infile.json')
    print('python3 -m ffuflags -i infile.json -p')
    print('python3 -m ffuflags -i infile.json -s')
    print('python3 -m ffuflags -i infile.json -c 401,403,404')



def main():
    global DEBUG
    global status_filters
    global filename
    opts, args = get_options(argv)
    handle_options(opts)

    if HELP:
        print_usage()
        exit(0)

    contents_json = loads( open(filename, 'r').read() )
    results = contents_json['results']
    [handle_result(r) for r in results]
    #handle_result(results[0])
    if DEBUG:
        print_debug(sortBy)     
    #a=printd(statuses, "-fc")
    #print(a, end=" ")
    a = printd(words_, '-fw')
    print(a, end=" ")
    a = printd(lines, '-fl')
    print(a, end=" ")
    a = printd(lengths, '-fs')
    print(a, end="")


if __name__ == '__main__':
    main()

