#!/usr/bin/env python

import argparse
import json
import os
import sys
import textwrap

from redis import StrictRedis
from plurmy import Slurm

def parse_args(args):
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='command')
    stage_doc = textwrap.dedent("""\

    The stage subcommand pushes messages to a user defined redis queue.
    The messages can be any serializable message, such as a file
    path, a WKT string, a PVL label, or a JSON message.

    Messages are staged using the redis pipeline capability so large
    numbers of messages (> 100k for example), can be efficiently pushed
    to the redis queue.
    
    The stage subcommand appends ':processing' to the queue name in
    order to make use of atomic push/pop operations if and when
    the process subcommand is executed. If one wishes to double check
    that messages have been pushed to their processing queue, it is necessary
    to append ':processing' to the queue name. See the example below.

    Usage Examples
    --------------
    $ ls *.img > mylist.lis
    $ plurmy stage <queuename> mylist.lis
      Pushed X messags to <queuename>:processing.
    $ redis-cli llen <queuename>:processing
      X (where X is the number of lines in mylist.lis)
    """)
    stage = subparsers.add_parser('stage', 
                                  help='Stage jobs to a processing queue', 
                                  formatter_class=argparse.RawDescriptionHelpFormatter,
                                  epilog=stage_doc)
    stage.add_argument('-p', '--port', help='The redis port. Alternatively, set the PLURMY_REDIS_PORT env variable', type=int)
    stage.add_argument('-o', '--host', help='The redis host to connect to. Alternatively, set the PLURMY_REDIS_HOST env variable.', default=None)
    stage.add_argument('queue', help='The name of the queue to stage work to.')
    stage.add_argument('inputfile', help='A text file delimited by a new line character containing the file to stage.')

    restage_doc = textwrap.dedent("""\
    This command moves messages from a <queuename>:working queue 
    back to the <queuename>:processing queue.
    
    When processing jobs from a processing queue on a large number
    of cores, it is highly likely that jobs will fail due to any 
    number of reasons. The plurmy command works by staging 
    messages to a processing queue and then atomically (without an
    opportunity for message lose) pushing those message to a working
    queue while processing is underway. At the conclusion of a successful
    job run, the message is removed (lrem) from the working queue. At 
    the conclusion of a long processing run with many jobs some number
    of jobs could remain on the working queue. 

    After messages have been restaged, it is highly likely that another
    processing run will be submitted using plurmy process.
    
    Usage Examples
    --------------
    $ plurmy restage <queuename>
      Moved X messages from <queuename>:working to <queuename>:processing
    """)

    restage = subparsers.add_parser('restage', 
                                    help='Restage failed jobs from a working queue to a processing queue.',
                                    formatter_class=argparse.RawDescriptionHelpFormatter,
                                    epilog=restage_doc)
    restage.add_argument('queue', help='The name of the queue to stage work to.')
    restage.add_argument('-p', '--port', help='The redis port. Alternatively, set the PLURMY_REDIS_PORT env variable', type=int)
    restage.add_argument('-o', '--host', help='The redis host to connect to. Alternatively, set the PLURMY_REDIS_HOST env variable.', default=None)
    process_doc = textwrap.dedent("""\
    The process subcommand is used to submit jobs that draw messages from a redis
    queue. The process command wraps a user provided command (a script or a 
    shell command most likely) and appends the message from the queue as the
    final argument.

    The script passed to the process subcommand (cmd) should be quoted
    as it is passed as a simple string. By default, process sets the number
    of tasks to one (-n=1). The command passed will be executed with 'srun -n 1 <cmd>'
    meaning that a single, non-parallel job will be executed, drawing messages
    from the processing queue. If the number of specified tasks is greater than one
    srun will execute n concurrent, tasks. For example, if -n=40, plurmy process
    will request 40 CPUs and execute 'srun -n 40 <cmd>'. A logic upper limit for n is the
    number of cores available on the cluster (Be kind to your neighbors...).

    The jobs submitted by plurmy process wrap the user supplied command in the following
    block:

    ```
    srun -n {args.ntasks} sh << EOF
    while :
      do
        msg=$(redis-cli -h {args.host} -p {args.port} rpoplpush {processing_queue_name} {working_queue_name})

        # When the queue is empty, break
        if [ -z "$msg" ]; 
        then 
          break 
        fi

        # Execute the passed command(s) 
        
        if . {args.cmd} $msg; then
            redis-cli -h ${args.host} -p ${args.port} lrem {working_queue_name} -1 "$msg"
        fi
      done
    EOF
    ```

    This block reads messages from the user supplied queue (e.g, do_things), atomically pushes the
    message to a working queue (e.g., do_things:working), executes the user supplied command, 
    and then, if successful, removes the message from the working queue.

    Assumptions
    -----------
    - the final positional argument passed to the command is the message
    - the command provides a non-zero exit code if it fails to execute properly
    - the command is wrapped in single quotes on submission as the parser parses it as a simple string
    - the queue is specified by the base name, e.g., my_queue and not my_queue:processing, the
      script appends :processing and :working to the user supplied queue name

    Usage Examples
    --------------
    In this first example 40 CPUs are requested with a 10 minute walltime and 4GB of RAM.
    Under this allocation, an srun command is submitted to run 40 concurrent tasks.
    
    plurmy process -j myjob -m 4000 -t '00:10:00' -n 40 myqueue 'my_awesome_script.sh <arg1> <arg2>'
    """)

    process = subparsers.add_parser('process', 
                                    help='Submit jobs to a cluster that draw from a queue.',
                                    formatter_class=argparse.RawDescriptionHelpFormatter,
                                    epilog=process_doc)
    process.add_argument('queue', help='The processing queue to draw messages from.')
    process.add_argument('cmd', help="The single quoted command to execute on each staged file.")
    process.add_argument('--notbashscript', action='store_true',
                         help='A flag to set if the script being passed is not a bash script.')
    process.add_argument('-e', '--env', help='An optional conda environment to activate', default=None)
    process.add_argument('-j', '--jobname', help='The name of the job.', default='plurmy')
    process.add_argument('-m', '--mem-per-cpu', help='The amount of RAM to request (in MB) per CPU.', 
                         default=2000, type=int)
    process.add_argument('-l', '--log-dir', help='Directory to place output logs.')
    process.add_argument('-n', '--ntasks', help='The number of CPUs to request.',
                         default=1, type=int)
    process.add_argument('-t', '--time', help='The amount of walltime to request.',
                        default="00:60:00")
    process.add_argument('--time-min', help='The minimum amount of walltime to run the job.',
                         default="00:30:00")
    process.add_argument('-p', '--port', help='The redis port. Alternatively, set the PLURMY_REDIS_PORT env variable', type=int)
    process.add_argument('-o', '--host', help='The redis host to connect to. Alternatively, set the PLURMY_REDIS_HOST env variable.', default=None)
    process.add_argument('-q', '--partition', help='The slurm processing queue to submit jobs to.')
    return parser, parser.parse_args(args)

def setup_redis_connection(host: str, port: int):
    """
    Setup a redis connection to the provided host and port. Default
    to using database 0.

    Parameters
    ----------
    host : str
           The IP or hostname where redis is running

    port : int
           The port that redis is listening at

    Returns
    -------
     : object
       A redis-py queue object
    """
    return StrictRedis(host=host, port=port, db=0)

def read_file(inputfile: str):
    """
    Read the lines of an input file into a list, running
    rstrip() on each line.

    Parameters
    ----------
    inputfile : str
                Path to the input file

    Returns
    -------
    iterable : list
               of strings where each entry is a line in the 
               input file
    """
    with open(inputfile, 'r') as stream:
        iterable = stream.readlines()
        iterable = [i.rstrip() for i in iterable]
    return iterable

def stage(redis_queue, iterable: list, processing_queue_name: str):
    """
    Stage an iterable of messages to a redis queue.

    Parameters
    ----------
    redis_ queue : object
                  A redis-py redis queue object

    iterable : list
               of serialized messages to push to the queue

    processing_queue_name : str
                            The name of the queue to pass the messages to

    """
    pipeline = redis_queue.pipeline()
    for i, msg in enumerate(iterable):
        pipeline.rpush(processing_queue_name, msg)
    pipeline.execute()
    print(f'Pushed {i+1} messages to {processing_queue_name}.')

def process(args, processing_queue_name: str, working_queue_name: str):
    """
    Submit jobs to a Slurm controller using sbatch directives to process data
    from a given processing queue.

    This func handles atomically pushing from the processing queue to the working
    queue and then popping messages off the working queue upon sucessful 
    completion.

    Parameters
    ----------
    args : object
           An argparse namespace with arguments to be parsed for job creation

    processing_queue_name : str
                            The name of the processing queue to draw work from

    working_queue_name : str
                         The name of the queue to push messages to while work is
                         underway.
    """

    if args.notbashscript == False:
      argscmd = f'. {args.cmd}'
    else:
      argscmd = args.cmd

    if args.env:
        env = f'conda activate --stack {args.env}'
    else:
        env = ''
    conda_init = os.environ.get('PLURMY_CONDA_INIT', None)
    if not conda_init:
        raise EnvironmentError('"PLURMY_CONDA_INIT" must be set to the path of the conda.sh script, e.g., /home/user/anaconda3/etc/profile.d/conda.sh')

    cmd = textwrap.dedent(f"""\
    srun bash <<'EOF'
    source {conda_init}
    conda activate plurmy
    {env}
    while :
      do
        msg=$(redis-cli -h {args.host} -p {args.port} rpoplpush {processing_queue_name} {working_queue_name})
        # When the queue is empty, break
        if [ -z "$msg" ]; then 
          break 
        fi

        # Execute the passed command(s); since this is executed in a subshell, the script could just use $msg. Explixit passing is preferred.
        
        if {argscmd} $msg; then
            redis-cli -h {args.host} -p {args.port} lrem {working_queue_name} -1 "$msg" > /dev/null
        fi
      done
    EOF
    """)

    submitter = Slurm(cmd,
                      job_name=args.jobname,
                      mem_per_cpu=args.mem_per_cpu,
                      time=args.time,
                      ntasks=args.ntasks,
                      output=args.log_dir,
                      account='astro',
                      partition=args.partition)
    job_str = submitter.submit()
    print(job_str)

def restage(redis_queue, processing_queue_name: str, working_queue_name: str):
    """
    Restage work from a working queue back onto a processing queue.

    Parameters
    ----------
    redis_ queue : object
                A redis-py redis queue object
   
    processing_queue_name : str
                            The name of the processing queue to draw work from

    working_queue_name : str
                         The name of the queue to push messages to while work is
                         underway. For restage these are, presumably, failed jobs
    """

    pipeline = redis_queue.pipeline()

    n_messages = redis_queue.llen(working_queue_name)
    for _ in range(n_messages):
        pipeline.rpoplpush(working_queue_name, processing_queue_name)
    pipeline.execute()
    print(f'Moved {n_messages} from {working_queue_name} to {processing_queue_name}.')

def get_queue_names(queue: str):
    """
    Generate working and processing queue names

    Parameters
    ----------
    queue : str
            The name of the queue

    Returns
    -------
      :
       Two strings with ':processing' and ':working' appended to 
       the input queue name
    """
    return f'{queue}:processing', f'{queue}:working'

def get_redis_host_port(args):
  """
  Argument validation to override the host/port if provided as arguments
  to this script. If the host/port arguments are not overridden, get the
  values from the environment and raise an error if still None.

  Parameters
  ----------
  args : object
         An argparse Namespace

  Returns
  -------
  host : str
         The redis hostname
  
  port : int
         The port redis is listening on
  """
  if args.host is None:
    host = os.environ.get('PLURMY_REDIS_HOST', None)
  else:
    host = args.host
  if args.port is None:
    port = os.environ.get('PLURMY_REDIS_PORT', None)
  else:
    port = args.port

  if host is None:
    raise ValueError(f'Redis host is {host}. A valid redis host must be set using either the --host argument or the PLURMY_REDIS_HOST environment variable.')
  if port is None:
    raise ValueError(f'Redis port is {port}. A valid redis port must be set using either the --port argument or the PLURMY_REDIS_PORT environment variable.')

  return host, int(port)

def main(parser=None, args=None):
    """
    The dispatcher for the job commands

    Parameters
    ----------
    parser : object
             An argparse ArgumentParser object

    args : object
           An argparse Namespace
    """
    if parser == None:
        parser, args = parse_args(sys.argv[1:])
    processing_queue_name, working_queue_name = get_queue_names(args.queue)

    host, port = get_redis_host_port(args)

    if args.command == 'stage':
        redis_queue = setup_redis_connection(host=host, port=port)
        iterable = read_file(args.inputfile)
        stage(redis_queue, iterable, processing_queue_name)
    elif args.command =='restage':
        redis_queue = setup_redis_connection(host=host, port=port)
        restage(redis_queue, processing_queue_name, working_queue_name)
    elif args.command == 'process':
        process(args, processing_queue_name, working_queue_name)
    else:
        parser.print_help()

if __name__ == '__main__':
    main(parse_args(sys.argv[1:]))
 
