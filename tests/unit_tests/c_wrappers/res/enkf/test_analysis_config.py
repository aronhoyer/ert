import pytest

from ert._c_wrappers.enkf import AnalysisConfig, ConfigKeys


@pytest.fixture
def analysis_config(minimum_case):
    return minimum_case.resConfig().analysis_config


def test_keywords_for_monitoring_simulation_runtime(analysis_config):

    # Unless the MIN_REALIZATIONS is set in config, one is required to
    # have "all" realizations.
    assert not analysis_config.have_enough_realisations(5)
    assert analysis_config.have_enough_realisations(10)

    analysis_config.set_max_runtime(50)
    assert analysis_config.get_max_runtime() == 50

    analysis_config.set_stop_long_running(True)
    assert analysis_config.get_stop_long_running()


def test_analysis_modules(analysis_config):
    assert analysis_config.activeModuleName() is not None
    assert analysis_config.getModuleList() is not None


def test_analysis_config_global_std_scaling(analysis_config):
    assert pytest.approx(analysis_config.get_global_std_scaling()) == 1.0
    analysis_config.set_global_std_scaling(0.77)
    assert pytest.approx(analysis_config.get_global_std_scaling()) == 0.77


def test_analysis_config_constructor(setup_case):
    res_config = setup_case("simple_config", "analysis_config")
    assert res_config.analysis_config == AnalysisConfig.from_dict(
        config_dict={
            ConfigKeys.NUM_REALIZATIONS: 10,
            ConfigKeys.ALPHA_KEY: 3,
            ConfigKeys.RERUN_KEY: False,
            ConfigKeys.RERUN_START_KEY: 0,
            ConfigKeys.UPDATE_LOG_PATH: "update_log",
            ConfigKeys.STD_CUTOFF_KEY: 1e-6,
            ConfigKeys.STOP_LONG_RUNNING: False,
            ConfigKeys.GLOBAL_STD_SCALING: 1,
            ConfigKeys.MAX_RUNTIME: 0,
            ConfigKeys.MIN_REALIZATIONS: 10,
            ConfigKeys.ANALYSIS_COPY: [
                {
                    ConfigKeys.SRC_NAME: "STD_ENKF",
                    ConfigKeys.DST_NAME: "ENKF_HIGH_TRUNCATION",
                }
            ],
            ConfigKeys.ANALYSIS_SET_VAR: [
                {
                    ConfigKeys.MODULE_NAME: "STD_ENKF",
                    ConfigKeys.VAR_NAME: "ENKF_NCOMP",
                    ConfigKeys.VALUE: 2,
                },
                {
                    ConfigKeys.MODULE_NAME: "ENKF_HIGH_TRUNCATION",
                    ConfigKeys.VAR_NAME: "ENKF_TRUNCATION",
                    ConfigKeys.VALUE: 0.99,
                },
            ],
            ConfigKeys.ANALYSIS_SELECT: "ENKF_HIGH_TRUNCATION",
        }
    )


@pytest.mark.parametrize(
    "num_realization, min_realizations, expected_min_real",
    [
        (80, "10%", 8),
        (5, "2%", 1),
        (8, "50%", 4),
        (8, "100%", 8),
        (8, "100%", 8),
        (8, "10%", 1),
        (80, 0, 80),
        (80, 0, 80),
        (900, None, 900),
        (900, 10, 10),
        (80, 50, 50),
        (80, 80, 80),
        (80, 100, 80),
    ],
)
def test_analysis_config_min_realizations(
    num_realization, min_realizations, expected_min_real
):
    config_dict = {
        ConfigKeys.NUM_REALIZATIONS: num_realization,
    }
    if min_realizations is not None:
        config_dict[ConfigKeys.MIN_REALIZATIONS] = min_realizations

    analysis_config = AnalysisConfig.from_dict(config_dict)

    assert analysis_config.minimum_required_realizations == expected_min_real


def test_analysis_config_stop_long_running():
    config_dict = {
        ConfigKeys.NUM_REALIZATIONS: 10,
    }
    analysis_config = AnalysisConfig.from_dict(config_dict)
    assert not analysis_config.get_stop_long_running()
    analysis_config.set_stop_long_running(True)
    assert analysis_config.get_stop_long_running()


def test_analysis_config_alpha():
    config_dict = {
        ConfigKeys.NUM_REALIZATIONS: 10,
    }
    analysis_config = AnalysisConfig.from_dict(config_dict)
    assert analysis_config.get_enkf_alpha() == 3.0
    analysis_config.set_enkf_alpha(42.0)
    assert analysis_config.get_enkf_alpha() == 42.0

    config_dict[ConfigKeys.ALPHA_KEY] = 24
    new_analysis_config = AnalysisConfig.from_dict(config_dict)
    assert new_analysis_config.get_enkf_alpha() == 24.0


def test_analysis_config_std_cutoff():
    config_dict = {
        ConfigKeys.NUM_REALIZATIONS: 10,
    }
    analysis_config = AnalysisConfig.from_dict(config_dict)
    assert analysis_config.get_std_cutoff() == 1e-06
    analysis_config.set_std_cutoff(42.0)
    assert analysis_config.get_std_cutoff() == 42.0

    config_dict[ConfigKeys.STD_CUTOFF_KEY] = 24
    new_analysis_config = AnalysisConfig.from_dict(config_dict)
    assert new_analysis_config.get_std_cutoff() == 24.0