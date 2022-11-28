from pathlib import Path

from ert._c_wrappers.config import ConfigParser, ContentTypeEnum
from ert._c_wrappers.enkf import ConfigKeys
from ert._c_wrappers.enkf._config_content_as_dict import (
    SINGLE_OCCURRENCE_SINGLE_ARG_KEYS,
    config_content_as_dict,
)
from ert._clib.config_keywords import init_user_config_parser


def test_config_content_as_dict(tmpdir):
    with tmpdir.as_cwd():
        conf = ConfigParser()
        existing_file_1 = "test_1.t"
        existing_file_2 = "test_2.t"
        Path(existing_file_2).write_text("something")
        Path(existing_file_1).write_text("not important")
        init_user_config_parser(conf)

        schema_item = conf.add("MULTIPLE_KEY_VALUE", False)
        schema_item.iset_type(0, ContentTypeEnum.CONFIG_INT)

        schema_item = conf.add("KEY", False)
        schema_item.iset_type(2, ContentTypeEnum.CONFIG_INT)

        with open("config", "w") as fileH:
            fileH.write(f"{ConfigKeys.NUM_REALIZATIONS} 42\n")
            fileH.write(f"{ConfigKeys.DATA_FILE} {existing_file_2} \n")
            fileH.write(f"{ConfigKeys.REFCASE} {existing_file_1} \n")

            fileH.write("MULTIPLE_KEY_VALUE 6\n")
            fileH.write("MULTIPLE_KEY_VALUE 24\n")
            fileH.write("MULTIPLE_KEY_VALUE 12\n")
            fileH.write("QUEUE_OPTION SLURM MAX_RUNNING 50\n")
            fileH.write("KEY VALUE1 VALUE1 100\n")
            fileH.write("KEY VALUE2 VALUE2 200\n")
        content = conf.parse("config")
        content_as_dict = config_content_as_dict(content, {})
        assert content_as_dict == {
            "KEY": [["VALUE1", "VALUE1", 100], ["VALUE2", "VALUE2", 200]],
            ConfigKeys.NUM_REALIZATIONS: 42,
            ConfigKeys.QUEUE_OPTION: [["SLURM", "MAX_RUNNING", "50"]],
            "MULTIPLE_KEY_VALUE": [[6], [24], [12]],
            ConfigKeys.DATA_FILE: str(Path.cwd() / existing_file_2),
            ConfigKeys.REFCASE: str(Path.cwd() / existing_file_1),
        }


SINGLE_OCCURRENCE_KEY_TYPES = {
    ConfigKeys.ALPHA_KEY: "int",
    ConfigKeys.ANALYSIS_SELECT: "str",
    ConfigKeys.CONFIG_DIRECTORY: "path",
    ConfigKeys.DATAROOT: "file_path",
    ConfigKeys.DATA_FILE: "file_path",
    ConfigKeys.ECLBASE: "file_path",
    ConfigKeys.ENSPATH: "path",
    ConfigKeys.GEN_KW_EXPORT_NAME: "str",
    ConfigKeys.GEN_KW_TAG_FORMAT: "str",
    ConfigKeys.GRID: "file_path",
    ConfigKeys.HISTORY_SOURCE: "history_enum",
    ConfigKeys.ITER_CASE: "str",
    ConfigKeys.ITER_COUNT: "int",
    ConfigKeys.ITER_RETRY_COUNT: "int",
    ConfigKeys.JOBNAME: "str",
    ConfigKeys.JOB_SCRIPT: "file_path",
    ConfigKeys.LICENSE_PATH: "file_path",
    ConfigKeys.MAX_RESAMPLE: "int",
    ConfigKeys.MAX_RUNTIME: "int",
    ConfigKeys.MAX_SUBMIT: "int",
    ConfigKeys.MIN_REALIZATIONS: "int",
    ConfigKeys.NUM_CPU: "int",
    ConfigKeys.NUM_REALIZATIONS: "int",
    ConfigKeys.OBS_CONFIG: "file_path",
    ConfigKeys.QUEUE_SYSTEM: "str",
    ConfigKeys.RANDOM_SEED: "str",
    ConfigKeys.REFCASE: "file_path",
    ConfigKeys.RERUN_KEY: "bool",
    ConfigKeys.RERUN_START_KEY: "int",
    ConfigKeys.RUNPATH: "path",
    ConfigKeys.RUNPATH_FILE: "file_path",
    ConfigKeys.STD_CUTOFF_KEY: "float",
    ConfigKeys.STOP_LONG_RUNNING: "bool",
    ConfigKeys.TIME_MAP: "file_path",
    ConfigKeys.UPDATE_LOG_PATH: "file_path",
}


def test_config_content_as_dict_single_value_keys(tmpdir):
    with tmpdir.as_cwd():
        conf = ConfigParser()
        existing_file_1 = "test_1.t"
        existing_file_2 = "test_2.t"
        Path(existing_file_2).write_text("something")
        Path(existing_file_1).write_text("not important")
        init_user_config_parser(conf)
        type_value_map = {
            "str": "abc",
            "path": tmpdir,
            "file_path": existing_file_1,
            "bool": "TRUE",
            "float": 4.2,
            "int": 2,
            "history_enum": "REFCASE_SIMULATED",
        }

        with open("config.file", "w") as fileH:
            for key in SINGLE_OCCURRENCE_SINGLE_ARG_KEYS:
                key_type = SINGLE_OCCURRENCE_KEY_TYPES[key]
                value = type_value_map[key_type]
                fileH.write(f"{key} {value}\n{key} {value}\n")

        content = conf.parse("config.file")
        content_as_dict = config_content_as_dict(content, {})
        for _, value in content_as_dict.items():
            assert not isinstance(value, list)


def test_that_as_dict_adds_site_config_first():
    user_config_content = {"SET_ENV": [["var2", "val2"]]}
    site_config_content = {"SET_ENV": [["var1", "val1"]]}
    assert config_content_as_dict(user_config_content, site_config_content) == {
        "SET_ENV": [["var1", "val1"], ["var2", "val2"]]
    }


def test_that_as_dict_joins_queue_option_values():
    assert config_content_as_dict(
        {
            ConfigKeys.QUEUE_OPTION: [
                ["queue_type", "opt", "rest", "of", "the", "values"]
            ]
        },
        {},
    ) == {ConfigKeys.QUEUE_OPTION: [["queue_type", "opt", "rest of the values"]]}