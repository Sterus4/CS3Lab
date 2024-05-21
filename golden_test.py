import contextlib
import io
import logging
import os
import tempfile

import pytest

from src import translator, machine


@pytest.mark.golden_test("golden/*.yml")
def test_whole_by_golden(golden, caplog):
    caplog.set_level(logging.DEBUG)

    with tempfile.TemporaryDirectory() as tmpdirname:
        source = os.path.join(tmpdirname, "program.txt")
        input_stream = os.path.join(tmpdirname, "input.txt")
        target = os.path.join(tmpdirname, "output.txt")

        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["in_source"])
        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["in_input"])

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main(source, target)
            print("============================================================")
            machine.main(target, input_stream)
        with open(target, encoding="utf-8", mode="r") as file:
            code = file.read()
        assert code == golden.out["out_code"]
        assert stdout.getvalue() == golden.out["out_output"]
        assert caplog.text[:min(len(caplog.text), 60000)] == golden.out["out_log"]
