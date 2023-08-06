import _pytest
import _pytest.python
import _pytest.terminal
import pytest

import pytest_spec2md.spec_creator


def pytest_addoption(parser):
    group = parser.getgroup('general')
    group.addoption(
        '--spec2md',
        action='store_true',
        dest='spec2md',
        help='Saves test results as specification document in markdown format.'
    )

    parser.addini(
        'spec_target_file',
        default='documentation/spec.md',
        help='The target file to save the generated specification.'
    )

    parser.addini(
        'spec_indent',
        default='  ',
        help='Indention of spec in console.'
    )


_act_config = None


def pytest_configure(config):
    global _act_config
    _act_config = config

    if config.option.spec2md:
        pytest_spec2md.spec_creator.SpecWriter.delete_existing_specification_file(config)

        config.addinivalue_line(
            "markers", "spec_reference(name, docstring): mark specification reference for the test"
        )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Adds docstring to the item usage in report"""
    outcome = yield
    pytest_spec2md.spec_creator.ItemEnhancer.enhance(outcome, item)


@pytest.hookimpl(trylast=True)
def pytest_runtest_logreport(report):
    if report.when == 'call':
        pytest_spec2md.spec_creator.SpecWriter.create_specification_document(
            config=_act_config, report=report)
