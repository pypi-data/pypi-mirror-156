import argparse
from unittest.mock import mock_open, patch, create_autospec
import pytest
import os

from plurmy import orchestrate as orc

import fakeredis

@pytest.mark.parametrize('args, expected',[
    (['stage', 'my_queue', 'my_input'], {'command':'stage', 'queue':'my_queue', 'inputfile':'my_input', 
                                         'host':None, 'port':None}),
    (['restage', 'my_queue'], {'command':'restage', 'queue':'my_queue', 'port':None,
                                      'host':None}),
    (['process', 'my_queue', 'cmd'], {'command':'process', 'queue':'my_queue', 'cmd':'cmd',
                                      'mem_per_cpu':2000, 'log_dir':None, 'ntasks':1,
                                      'time':'00:60:00', 'time_min':'00:30:00', 'port':None,
                                      'host':None, 'jobname':'plurmy',
                                      'notbashscript':False, 'env':None}),
    (['process', 'my_queue', 'cmd', '-j', 'foo'], {'command':'process', 'queue':'my_queue', 'cmd':'cmd',
                                      'mem_per_cpu':2000, 'log_dir':None, 'ntasks':1,
                                      'time':'00:60:00', 'time_min':'00:30:00', 'port':None,
                                      'host':None, 'jobname':'foo',
                                      'notbashscript':False, 'env':None}),
    (['process', 'my_queue', 'cmd', '-m', '4000'], {'command':'process', 'queue':'my_queue', 'cmd':'cmd',
                                      'mem_per_cpu':4000, 'log_dir':None, 'ntasks':1,
                                      'time':'00:60:00', 'time_min':'00:30:00', 'port':None,
                                      'host':None, 'jobname':'plurmy',
                                      'notbashscript':False, 'env':None}),
    (['process', 'my_queue', 'cmd', '-l', '/here'], {'command':'process', 'queue':'my_queue', 'cmd':'cmd',
                                      'mem_per_cpu':2000, 'log_dir':'/here', 'ntasks':1,
                                      'time':'00:60:00', 'time_min':'00:30:00', 'port':None,
                                      'host': None, 'jobname':'plurmy',
                                      'notbashscript':False, 'env':None}),
    (['process', 'my_queue', 'cmd', '-n', '40'], {'command':'process', 'queue':'my_queue', 'cmd':'cmd',
                                      'mem_per_cpu':2000, 'log_dir':None, 'ntasks':40,
                                      'time':'00:60:00', 'time_min':'00:30:00', 'port':None,
                                      'host':None, 'jobname':'plurmy',
                                      'notbashscript':False, 'env':None}),
    (['process', 'my_queue', 'cmd', '-t', '00:15:00'], {'command':'process', 'queue':'my_queue', 'cmd':'cmd',
                                      'mem_per_cpu':2000, 'log_dir':None, 'ntasks':1,
                                      'time':'00:15:00', 'time_min':'00:30:00', 'port':None,
                                      'host':None, 'jobname':'plurmy',
                                      'notbashscript':False, 'env':None}), 
    (['process', 'my_queue', 'cmd', '--time-min', '00:60:00'], {'command':'process', 'queue':'my_queue', 'cmd':'cmd',
                                      'mem_per_cpu':2000, 'log_dir':None, 'ntasks':1,
                                      'time':'00:60:00', 'time_min':'00:60:00', 'port':None,
                                      'host':None, 'jobname':'plurmy',
                                      'notbashscript':False, 'env':None}), 
    (['process', 'my_queue', 'cmd', '--port', '4000'], {'command':'process', 'queue':'my_queue', 'cmd':'cmd',
                                      'mem_per_cpu':2000, 'log_dir':None, 'ntasks':1,
                                      'time':'00:60:00', 'time_min':'00:30:00', 'port':4000,
                                      'host':None, 'jobname':'plurmy',
                                      'notbashscript':False, 'env':None}), 
    (['process', 'my_queue', 'cmd', '--host', 'host'], {'command':'process', 'queue':'my_queue', 'cmd':'cmd',
                                      'mem_per_cpu':2000, 'log_dir':None, 'ntasks':1,
                                      'time':'00:60:00', 'time_min':'00:30:00', 'port':None,
                                      'host':'host', 'jobname':'plurmy',
                                      'notbashscript':False, 'env':None}),  
    (['process', 'my_queue', 'cmd', '--notbashscript'], {'command':'process', 'queue':'my_queue', 'cmd':'cmd',
                                      'mem_per_cpu':2000, 'log_dir':None, 'ntasks':1,
                                      'time':'00:60:00', 'time_min':'00:30:00', 'port':None,
                                      'host':None, 'jobname':'plurmy',
                                      'notbashscript':True, 'env':None}),                                                                                                                                                                                          
])
def test_parse_args(args, expected):
    parser, args = orc.parse_args(args)
    expected = argparse.Namespace(**expected)
    assert args == expected

@pytest.mark.parametrize('args, expected', [
    (['-h'], '{stage,restage,process}'),
    (['stage', '-h'], 'plurmy stage <queuename> mylist.lis'),
    (['restage', '-h'], 'plurmy restage <queuename>'),
    (['process', '-h'], 'plurmy process -j myjob -m 4000')
])
def test_print_help(capfd, args, expected):
    with pytest.raises(SystemExit):
        parser, args = orc.parse_args(args)
    out, err = capfd.readouterr()
    assert expected in out

def test_setup_redis_connection():
    def mock_redis_constructor(host=None, port=None, db=0):
        pass
    
    with patch('plurmy.orchestrate.StrictRedis', create_autospec(mock_redis_constructor)) as _conn:
        orc.setup_redis_connection('host', 12345)
        _conn.assert_called_once_with('host', 12345, db=0)

def test_readfile():
    with patch('plurmy.orchestrate.open', mock_open()) as _file:
        iterable = orc.read_file('foo.lis')
        _file.assert_called_once_with('foo.lis', 'r')
    
def test_stage():
    redis_queue = fakeredis.FakeStrictRedis()
    iterable = ['fee', 'fi', 'fo', 'fum']
    orc.stage(redis_queue, iterable, 'test_stage_queue')
    assert len(iterable) == redis_queue.llen('test_stage_queue')

    for i in range(len(iterable)):
        # Need to encode because redis strings are binary
        assert redis_queue.lpop('test_stage_queue') == iterable[i].encode()

@pytest.mark.parametrize('args, env, expected_host, expected_port', [
    (argparse.Namespace(host=None, port=None), {'PLURMY_REDIS_HOST':'localhost', 'PLURMY_REDIS_PORT':'1000'}, 'localhost', 1000),
    (argparse.Namespace(host='foo', port=None), {'PLURMY_REDIS_HOST':'notfoo', 'PLURMY_REDIS_PORT':'6379'}, 'foo', 6379),
    (argparse.Namespace(host=None, port=1000), {'PLURMY_REDIS_HOST':'localhost', 'PLURMY_REDIS_PORT':'6379'}, 'localhost', 1000)
])
def test_get_redis_host_port(args, env, expected_host, expected_port):
    
    with patch.dict(os.environ, env):
        host, port = orc.get_redis_host_port(args)
        assert host == expected_host
        assert port == expected_port

@pytest.mark.parametrize('args, env, errmsg', [
    (argparse.Namespace(host=None, port=None), {}, 'host'),
    (argparse.Namespace(host='foo', port=None), {}, 'port'),
])
def test_raise_redis_host_port(args, env, errmsg):
    with patch.dict(os.environ, env, clear=True):
        with pytest.raises(ValueError) as e:
            host, port = orc.get_redis_host_port(args)
        assert errmsg in str(e.value)

@pytest.mark.parametrize('args, cmd, env', [
    (argparse.Namespace(jobname='test', mem_per_cpu=2000, time='00:05:00', ntasks=1, 
                        log_dir=None, host='localhost', port=6547, cmd='my_custom_command',
                        notbashscript=False, env=None), '. my_custom_command', ''),
    (argparse.Namespace(jobname='test', mem_per_cpu=2000, time='00:05:00', ntasks=1, 
                        log_dir=None, host='localhost', port=6547, cmd='my_custom_command',
                        notbashscript=True, env=None), 'my_custom_command', ''),
    (argparse.Namespace(jobname='test', mem_per_cpu=2000, time='00:05:00', ntasks=1, 
                        log_dir=None, host='localhost', port=6547, cmd='my_custom_command',
                        notbashscript=True, env='/my/conda/env'), 'my_custom_command', 'conda activate --stack /my/conda/env')

])
def test_process(capfd, args, cmd, env):    
    with patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value.communicate.return_value = ('', '')

        orc.process(args, 'processing_queue', 'working_queue')
    out, err = capfd.readouterr()
    assert 'if [ -z "$msg" ]; then' in out
    assert f'if {cmd} $msg; then' in out
    assert 'srun' in out
    assert env in out

def test_restage():
    redis_queue = fakeredis.FakeStrictRedis()
    working_queue_name = 'test_restage:working'
    processing_queue_name = 'test_restage:processing'
    redis_queue.rpush(working_queue_name, 'Fake Message')
    assert redis_queue.llen(working_queue_name) == 1

    orc.restage(redis_queue, processing_queue_name, working_queue_name)

    assert redis_queue.llen(working_queue_name) == 0
    assert redis_queue.llen(processing_queue_name) == 1

def test_get_queue_names():
    processing, working = orc.get_queue_names('queue')
    assert processing == 'queue:processing'
    assert working == 'queue:working'

@pytest.mark.parametrize('cmd', [
    ('stage'),
    ('restage'),
    ('process')
])
def test_main(capfd, cmd):
    parser = argparse.ArgumentParser()
    args = argparse.Namespace(command=cmd, queue='queue', 
                              host='localhost', port=6547,
                              inputfile='/foo')
    if cmd == 'stage':
        # Have to mock the read_file call
        with patch('plurmy.orchestrate.read_file', lambda x: []) as rf:
            with patch(f'plurmy.orchestrate.{cmd}', create_autospec(lambda x, y, z:x)) as _func:
                orc.main(parser, args)
                _func.assert_called_once()
    else:
        # Have to mock the redis setup call
        def mock_redis_constructor(host=None, port=None, db=0):
            pass
    
        with patch('plurmy.orchestrate.StrictRedis', create_autospec(mock_redis_constructor)) as _conn:
            orc.setup_redis_connection('host', 12345)
            with patch(f'plurmy.orchestrate.{cmd}', create_autospec(lambda x, y, z:x)) as _func:
                orc.main(parser, args)
                _func.assert_called_once()