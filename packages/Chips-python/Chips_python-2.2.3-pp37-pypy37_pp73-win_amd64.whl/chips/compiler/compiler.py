#!/usr/bin/env python
"""A C to Verilog compiler"""

__author__ = "Jon Dawson"
__copyright__ = "Copyright (C) 2013, Jonathan P Dawson"
__version__ = "0.1"

import sys

from chips.compiler.parser import Parser
from chips.compiler.exceptions import C2CHIPError
from chips.compiler.macro_expander import expand_macros
from chips.compiler.verilog_area import generate_CHIP as generate_CHIP_area
from chips.compiler.python_model import generate_python_model
from . import fpu


def generate_library():
    output_file = open("chips_lib.v", "w")
    output_file.write(fpu.adder)
    output_file.write(fpu.divider)
    output_file.write(fpu.multiplier)
    output_file.write(fpu.double_divider)
    output_file.write(fpu.double_multiplier)
    output_file.write(fpu.double_adder)
    output_file.write(fpu.int_to_float)
    output_file.write(fpu.float_to_int)
    output_file.write(fpu.long_to_double)
    output_file.write(fpu.double_to_long)
    output_file.write(fpu.float_to_double)
    output_file.write(fpu.double_to_float)
    output_file.close()


def comp(input_file, options={}, parameters={}, sn=None):

    reuse = "no_reuse" not in options
    initialize_memory = "no_initialize_memory" not in options
    generate_library()

    try:
        # Optimize for area
        parser = Parser(input_file, reuse, initialize_memory, parameters)
        process = parser.parse_process()
        if sn is not None:
            name = process.main.name + "_%s" % sn
        else:
            name = process.main.name

        instructions = process.generate()
        instructions = expand_macros(instructions, parser.allocator)
        if "dump" in options:
            for i in instructions:
                print((
                    i.get("op", "-"),
                    i.get("z", "-"),
                    i.get("a", "-"),
                    i.get("b", "-"),
                    i.get("literal", "-"),
                    i.get("trace"),
                ))
        output_file = name + ".v"
        output_file = open(output_file, "w")
        inputs, outputs = generate_CHIP_area(
            input_file,
            name,
            instructions,
            output_file,
            parser.allocator,
            initialize_memory,
            int(options.get("memory_size", 4096)))
        output_file.close()

    except C2CHIPError as err:
        print("Error in file:", err.filename, "at line:", err.lineno)
        print(err.message)
        sys.exit(-1)

    return name, inputs, outputs, ""


def compile_python_model(
        input_file,
        options={},
        parameters={},
        inputs={},
        outputs={},
        debug=False,
        profile=False,
        sn=0,
):

    generate_library()

    try:
        # Optimize for area
        parser = Parser(input_file, False, False, parameters)
        process = parser.parse_process()
        name = process.main.name + "_%u" % sn
        instructions = process.generate()
        instructions = expand_macros(instructions, parser.allocator)
        if "dump" in options:
            for i in instructions:
                print(i)

        debug = debug or ("debug" in options)
        profile = profile or ("profile" in options)
        model = generate_python_model(
            debug,
            input_file,
            name,
            instructions,
            parser.allocator,
            inputs,
            outputs,
            profile)

        return (
            model,
            list(parser.allocator.input_names.values()),
            list(parser.allocator.output_names.values()),
            name
        )

    except C2CHIPError as err:
        print("Error in file:", err.filename, "at line:", err.lineno)
        print(err.message)
        sys.exit(-1)
