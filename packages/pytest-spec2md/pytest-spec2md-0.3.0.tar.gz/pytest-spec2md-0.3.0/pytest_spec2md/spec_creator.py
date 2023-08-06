import datetime
import importlib
import os
import inspect
import typing

import _pytest.reports
import pytest


class TestcaseSorter:

    def __init__(self, items: typing.List[pytest.Item]):
        self._items = items

    @staticmethod
    def split_name_of_item_by_path(item: pytest.Item):
        return item.nodeid.split('::', maxsplit=1)

    @staticmethod
    def rename_for_sorting(entry: str, splitter: str = '/'):
        depth = entry.count(splitter)
        if depth == 0:
            return f'{0}_'
        split_entry = entry.split(splitter)
        return '1_' + "_1_".join(split_entry[:-1]) + f'{splitter}{0}_'

    def sort_by_layer(self):
        self._items.sort(
            key=lambda x:
            self.rename_for_sorting(self.split_name_of_item_by_path(x)[0]) +
            self.rename_for_sorting(self.split_name_of_item_by_path(x)[1], '::')
        )

    @property
    def items(self):
        return self._items


class SpecWriter:
    _act_writer: 'SpecWriter' = None

    def __init__(self, filename: str):
        self._last_parents: list = []
        self._last_node_content: _pytest.reports.TestReport = None
        self._filename = filename
        self._create_spec_file_if_not_exists()

    @property
    def filename(self):
        return self._filename

    @classmethod
    def delete_existing_specification_file(cls, config):
        filename = config.getini('spec_target_file')
        if os.path.exists(filename):
            os.remove(filename)

        cls._act_writer = None

    @classmethod
    def create_specification_document(cls, config, report: _pytest.reports.TestReport):
        if SpecWriter._act_writer is None:
            filename = config.getini('spec_target_file')
            cls._act_writer = SpecWriter(os.path.join(os.getcwd(), filename))

        cls._act_writer.write_node_to_file(report)

    def _create_spec_file_if_not_exists(self):
        if not os.path.exists(self.filename):
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)

            with open(self.filename, 'w') as file:
                file.writelines([
                    '# Specification\n',
                    'Automatically generated using pytest_spec2md  \n'
                    f'Generated: {datetime.datetime.now()}  \n'
                    f'\n',
                ])

    @staticmethod
    def split_scope(test_node):
        data = [i for i in test_node.split('::') if i != '()']
        if data[-1].endswith("]"):
            data[-1] = data[-1].split("[")[0]
        return data

    @staticmethod
    def format_test_name(name: str):
        if name is not str:
            name = str(name)
        if name.endswith("["):
            name = name[:name.find("[")]
        return name.replace('test_', '', 1).replace('_', ' ')

    @staticmethod
    def format_class_name(name: str):
        if name is not str:
            name = str(name.__name__)
        name = name.replace('Test', '', 1)
        return ''.join(' ' + x if x.isupper() else x for x in name)

    @staticmethod
    def format_doc_string(doc_string: str):
        if not doc_string:
            return []
        return [x.strip() for x in doc_string.split("\n") if x.strip()]

    def write_node_to_file(self, node_content: _pytest.reports.TestReport):
        self._create_spec_file_if_not_exists()

        parents = getattr(node_content, "node_parents", [])

        last_module = self.split_scope(self._last_node_content.nodeid)[0] if self._last_node_content else ""
        act_module = self.split_scope(node_content.nodeid)[0]

        last_tc_name = self.split_scope(self._last_node_content.nodeid)[-1] if self._last_node_content else ""
        act_tc_name = self.split_scope(node_content.nodeid)[-1]

        longnewline = "  \n  "
        shortnewline = "\n"
        print_testcase = False

        with open(self.filename, 'a') as file:
            if not last_module or last_module != act_module:  # changed test file
                self._write_module_info_to_file(act_module, file)

            if len(parents) == 0:
                if last_module != act_module:
                    file.write(
                        f'\n'
                        f'### General\n'
                        f'\n'
                    )
                    print_testcase = True
            else:
                show_recursive = False
                line_start = '###'
                last_parents = self._last_parents.copy()
                last_parents.extend(["" for _ in range(len(parents) - len(last_parents))])
                for act, last in zip(parents, last_parents):
                    if show_recursive or act != last:
                        show_recursive = True
                        doc_lines = self.format_doc_string(getattr(act, "__doc__"))
                        file.write(
                            f'\n'
                            f'{line_start}{self.format_class_name(act)}\n' +
                            (f'  {shortnewline.join(doc_lines)}  \n' if doc_lines else '')
                        )
                        self._write_references(node_content, act, file)
                        file.write(f'\n')

                        print_testcase = True
                    line_start += '#'

            if print_testcase or act_tc_name != last_tc_name:
                tc = getattr(node_content, "node_obj", None)
                doc_lines = self.format_doc_string(getattr(tc, "__doc__"))

                file.write(
                    f' - **{self.format_test_name(act_tc_name)}**  \n' +
                    (f'  {longnewline.join(doc_lines)}\n' if doc_lines else '')
                )
                self._write_references(node_content, tc, file)

        self._last_parents = parents
        self._last_node_content = node_content

    def _write_module_info_to_file(self, act_module, file):
        module_name = act_module.replace('/', '.')[:-3]
        mod = importlib.import_module(module_name)
        doc_lines = self.format_doc_string(mod.__doc__)
        shortnewline = "\n"

        file.write(
            f'## Spec from {act_module}\n' +
            (f'{shortnewline.join(doc_lines)}  \n' if doc_lines else '')
        )

    def _write_references(self, node_content, act_obj, file):
        longnewline = "  \n  "
        references = getattr(node_content, "reference_docs", [])
        for target, reference in references:
            if target.obj == act_obj:
                file.write(
                    (f'  Tests: *{reference[0]}*  \n' if reference[0] else '') +
                    (f'  {longnewline.join(self.format_doc_string(reference[1]))}\n' if len(reference) > 1 else '')
                )


class ItemEnhancer:

    @classmethod
    def enhance(cls, outcome, item):
        report = outcome.get_result()  # type: _pytest.reports.TestReport
        node = getattr(item, 'obj', None)
        if node:
            report.node_obj = node
            report.node_parents = []
            parent = cls.get_parent(node)
            while parent:
                report.node_parents.append(parent)
                parent = cls.get_parent(parent)
            report.node_parents.reverse()

            report.reference_docs = []
            for marker in item.iter_markers_with_node(name='spec_reference'):
                report.reference_docs.append((marker[0], marker[1].args))

    @staticmethod
    def get_parent(obj):
        try:
            parents = obj.__qualname__.split(".")
            if len(parents) > 1 and "<locals>" not in parents:
                full_name = obj.__module__ + "." + ".".join(parents[:-1])
                script = \
                    f'exec("import {obj.__module__}") or {full_name}'
                x = eval(script, globals(), locals())
                return x

        except Exception as err:
            print(err)

        return None

    @staticmethod
    def _get_parent_doc(function):
        func = getattr(function, "__self__", None)
        if not func:
            return ""
        parent = getattr(func, "__class__", None)
        if not parent:
            return ""

        doc = inspect.getdoc(parent)
        return doc if doc is not None else ""
