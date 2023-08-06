from unittest import mock

import pytest
import plurmy


@pytest.fixture
def job():
    return plurmy.Slurm(
        "foo",
        job_name="SpecialJob",
        time="00:00:60",
        output="/mi/casa",
        mem_per_cpu="4096",
        partition="longall",
    )


@pytest.mark.parametrize(
    "time, expected",
    [
        ("1:00:00", 3600),
        ("01:00:00", 3600),
        ("00:01:00", 60),
        ("00:00:60", 60),
        ("00:00:90", 90),
    ],
)
def test_slurm_walltime_to_seconds(time, expected):
    print(plurmy.__file__)

    assert plurmy.slurm_walltime_to_seconds(time) == expected


@pytest.mark.parametrize(
    "command, output, err, kwargs, expected",
    [
        ("foo", "", None, {}, "foo"),  # Check command is passing
        ("foo", "", None, {"name": "SpecialJob"}, "SpecialJob"),
        ("foo", "", None, {"time": "00:00:60"}, "00:00:60"),
        ("foo", "", None, {"outdir": "/mi/casa"}, "/mi/casa"),
        ("foo", "", None, {"mem": 4096}, "4096"),
        ("foo", "", None, {"queue": "longall"}, "longall"),
        ("foo", "", None, {"ntasks": 3}, "--ntasks=3"),
        ("source activate krc\nfoo", "", None, {"env": "krc"}, "krc"),
        ("foo", "", "error", {}, "error"),
    ],
)
def test_spawn(job, command, output, err, kwargs, expected):
    job.command = command
    for k, v in kwargs.items():
        setattr(job, k, v)
    with mock.patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value.communicate.return_value = (output, err)
        js = job.submit()
        if err is None:
            assert expected in js
        else:
            assert js is False


@pytest.mark.parametrize(
    "command, array, output, err, kwargs, expected",
    [
        ("foo", "1-2", "", None, {}, "foo"),  # Check command is passing
        ("foo", "1-50", "", None, {"outdir": "/mi/casa"}, "/mi/casa"),
        ("foo", "1-6", "", None, {"queue": "longall"}, "longall"),
        ("source activate krc\nfoo", "1-6", "", None, {"env": "krc"}, "krc"),
        ("foo", "1-2", "", "error", {}, "error"),
        ("foo", "1-2", "", None, {"spread_job": ""}, "spread-job"),
    ],
)
def test_simple_job_arr(job, command, array, output, err, kwargs, expected):
    for k, v in kwargs.items():
        setattr(job, k, v)

    with mock.patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value.communicate.return_value = (output, err)

        js = job.submit(array=array)
        if err is None:
            call = mock.call(["sbatch", "--array", array], stdin=-1, stdout=-1)
            assert mock_popen.call_args_list == [call]
            assert len(js) == 1
            assert expected in js[0]
        else:
            assert js is False


@pytest.mark.parametrize(
    "command, array, output, err, nchunks, kwargs, expected",
    [
        ("foo", "1-400%2", "", None, 1, {"time": "00:00:60"}, "00:00:60"),
        ("foo", "1-1500", "", None, 2, {}, "foo"),
        ("foo", "1-1500%500", "", None, 2, {}, "foo"),
        ("foo", "1-2003%250", "", None, 3, {}, "foo"),
    ],
)
def test_chunked_job_arr(job, command, array, output, err, nchunks, kwargs, expected):
    for k, v in kwargs.items():
        setattr(job, k, v)

    with mock.patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value.communicate.return_value = (output, err)

        js = job.submit(array=array)

        if err is None:
            assert len(js) == nchunks
            for i in range(nchunks):
                assert expected in js[i]

        else:
            assert js is False


@pytest.mark.parametrize(
    "command, array, output, err, kwargs, expected",
    [("foo", "1-3,5-8", "", None, {"name": "SpecialJob"}, "SpecialJob")],
)
def test_compound_job_array(job, command, array, output, err, kwargs, expected):

    for k, v in kwargs.items():
        setattr(job, k, v)

    with mock.patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value.communicate.return_value = (output, err)

        js = job.submit(array=array)
        if err is None:
            calls = []

            for arr in array.split(","):
                calls.append(mock.call(["sbatch", "--array", arr], stdin=-1, stdout=-1))

            for i in range(len(calls)):
                assert mock_popen.call_args_list[i] == calls[i]
            for j in js:
                assert expected in j
        else:
            assert js is False
