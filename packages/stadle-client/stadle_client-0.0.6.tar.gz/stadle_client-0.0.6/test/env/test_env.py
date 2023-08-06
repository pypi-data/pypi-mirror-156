import os
import stadle

ENV_HANDLER = stadle.env_handler


def test_default_env_configs():
    current_working_dir = os.getcwd()

    expected_default_module_path = os.path.join(current_working_dir, "stadle")
    expected_default_config_path = os.path.join(expected_default_module_path, "configs")

    assert expected_default_module_path == ENV_HANDLER.module_path
    assert expected_default_config_path == ENV_HANDLER.config_path


def test_custom_env_configs():
    STADLE_CONFIG_PATH = os.path.join(os.getcwd(), "test", "test_data", "setups")
    agent_path = os.path.join(STADLE_CONFIG_PATH, "config_agent.json")
    expected_agent_config_path = agent_path
    from stadle.lib.util.helpers import set_env_config
    from stadle import EnvironmentVar
    set_env_config(config_type=EnvironmentVar.STADLE_AGENT_CONFIG_PATH, value=expected_agent_config_path)
    assert ENV_HANDLER.get_variable(
        EnvironmentVar.STADLE_AGENT_CONFIG_PATH.value) == expected_agent_config_path, "The environmental variable set wrong"