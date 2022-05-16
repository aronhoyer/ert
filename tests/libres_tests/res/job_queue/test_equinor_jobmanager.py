import json
import os
import os.path
import socket

import pytest
from libres_utils import ResTest

# Test data generated by ForwardModel
JSON_STRING = """
{
  "umask" : "0000",
  "jobList" : [ {"name" : "PERLIN",
  "executable" : "perlin.py",
  "target_file" : "my_target_file",
  "error_file" : "error_file",
  "start_file" : "some_start_file",
  "stdout" : "perlin.stdoit",
  "stderr" : "perlin.stderr",
  "stdin" : "intput4thewin",
  "argList" : ["-speed","hyper"],
  "environment" : {"TARGET" : "flatland"},
  "license_path" : "this/is/my/license/PERLIN",
  "max_running_minutes" : 12,
  "max_running" : 30
},
{"name" : "PERGEN",
  "executable" : "pergen.py",
  "target_file" : "my_target_file",
  "error_file" : "error_file",
  "start_file" : "some_start_file",
  "stdout" : "perlin.stdoit",
  "stderr" : "perlin.stderr",
  "stdin" : "intput4thewin",
  "argList" : ["-speed","hyper"],
  "environment" : {"TARGET" : "flatland"},
  "license_path" : "this/is/my/license/PERGEN",
  "max_running_minutes" : 12,
  "max_running" : 30
}]
}
"""


def gen_area_name(base, f):
    return base + "_" + f.func_name.split("_")[-1]


def create_jobs_py(jobList):
    jobs_file = os.path.join(os.getcwd(), "jobs.py")
    compiled_jobs_file = jobs_file + "c"

    for fname in [jobs_file, compiled_jobs_file]:
        if os.path.isfile(fname):
            os.unlink(fname)

    with open(jobs_file, "w") as f:
        f.write("jobList = ")
        f.write(json.dumps(jobList, indent=1))
        f.write("\n")

    return jobs_file


def create_jobs_json(jobList, umask="0000"):
    data = {"umask": umask, "jobList": jobList}

    jobs_file = os.path.join(os.getcwd(), "jobs.json")
    with open(jobs_file, "w") as f:
        f.write(json.dumps(data), indent=1)


@pytest.mark.equinor_test
class JobManagerEquinorTest(ResTest):
    def assert_ip_address(self, ip):
        try:
            socket.inet_aton(ip)
        except Exception as err:
            self.assertTrue(False, msg=f"On input {ip}: {err}.")  # noqa
