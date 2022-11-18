#!/usr/bin/env python


# ******************************************************
# * Copyright (C) 2022 the GLeeFuzz authors.
# * This file is part of GLeeFuzz.
# *
# * GLeeFuzz is free software: you can redistribute it
# * and/or modify it under the terms of the GNU General 
# * Public License as published by the Free Software 
# * Foundation, either version 3 of the License, or 
# * (at your option) any later version.
# *
# * GLeeFuzz is distributed in the hope that it will 
# * be useful, but WITHOUT ANY WARRANTY; without even
# * the implied warranty of MERCHANTABILITY or FITNESS
# * FOR A PARTICULAR PURPOSE. See the GNU General 
# * Public License for more details.
# *
# * You should have received a copy of the GNU 
# * General Public License along with GLeeFuzz. If not,
# * see <https://www.gnu.org/licenses/>.
# ******************************************************


import sys
import os
import pickle
import argparse
import random

from program.shader.shader_src import ShaderSrc, ShaderGroup


def extract_attribute_or_uniform_info(line):
    line = line.strip()
    splits = line.split(" ")
    t = splits[1]
    name = splits[2]
    name = name[:len(name) - 1]

    return t, name

def extract_shaders_from_file(src_file):

    BEGIN_PROG_MARKER = "__BEGINPROGRAM__"
    END_PROG_MARKER   = "__ENDPROGRAM__"
    VERTEX_SHADER_MARKER     = "__VERTEXSHADER__"
    FRAGMENT_SHADER_MARKER   = "__FRAGMENTSHADER__"
    RAND_PLACEHOLER = "PROGRAM_CACHE_BREAKER_RANDOM"
    ret = []
    with open(src_file, "r") as inf:
        while True:
            v_shader_lines = []
            f_shader_lines = []
            uniforms = []
            attributes = []

            ll = inf.readline()
            if ll == "":
                break
            l = ll.strip()
            while l != BEGIN_PROG_MARKER:
                l = inf.readline().strip()

            l = inf.readline().strip()
            while l != VERTEX_SHADER_MARKER:
                l = inf.readline().strip()

            l = inf.readline().strip()
            while l != FRAGMENT_SHADER_MARKER:
                if l != "":
                    v_shader_lines.append(l)
                    if l.startswith("in") or l.startswith("attribute"):
                        t, name = extract_attribute_or_uniform_info(l)
                        if name not in attributes:
                            attributes.append((name, t))

                    elif l.startswith("uniform"):
                        t, name = extract_attribute_or_uniform_info(l)
                        if name not in uniforms:
                            uniforms.append((name, t))

                l = inf.readline().strip()

            l = inf.readline().strip()
            while l != END_PROG_MARKER:
                if l != "":
                    f_shader_lines.append(l)
                    if l.startswith("in") or l.startswith("attribute"):
                        t, name = extract_attribute_or_uniform_info(l)
                        if name not in attributes:
                            attributes.append((name, t))

                    elif l.startswith("uniform"):
                        t, name = extract_attribute_or_uniform_info(l)
                        if name not in uniforms:
                            uniforms.append((name, t))

                l = inf.readline().strip()

            ####a program has been read
            r = random.random()
            v_shader_src = "\n".join(v_shader_lines).replace(RAND_PLACEHOLER, str(r))
            f_shader_src = "\n".join(f_shader_lines).replace(RAND_PLACEHOLER, str(r))

            print("============= BEGIN vertex shader ======================")
            print(v_shader_src)
            print("============= END vertex shader ======================")
            print("============= BEGIN fragment shader ======================")
            print(f_shader_src)
            print("============= END fragment shader ======================")
            
            v_shader = ShaderSrc(ShaderSrc.VERTER_SHADER, v_shader_src, 1)
            f_shader = ShaderSrc(ShaderSrc.FRAGMENT_SHADER, f_shader_src, 1)

            grp = ShaderGroup(v_shader, f_shader)
            grp.attributes = attributes
            grp.uniforms = uniforms
            ret.append(grp)
    return ret

def main():

    parser = argparse.ArgumentParser(prog="generate_shader_data",
                                     description="A tool for generating serialized shader programs")
    parser.add_argument("--sp_file", type=str, help="Where to write the serialized data")
    parser.add_argument("--output", required=True, type=str, help="Where to write the serialized data")
    args = parser.parse_args()

    v_src1 = "\n".join([
        "attribute vec4 aPosition;",
        "uniform vec4 u_offset;",
        "varying vec4 vColor;",
        "void main()",
        "{",
        "   gl_Position = aPosition + u_offsets;",
        "   vec2 texcoord = vec2(aPosition.xy * 0.5 + vec2(0.5, 0.5));",
        "   vColor = vec4(",
        "       texcoord,",
        "       texcoord.x * texcoord.y,",
        "       (1.0 - texcoord.x) * texcoord.y * 0.5 + 0.5);",
        "}"
    ]);
    v_shader = ShaderSrc(ShaderSrc.VERTER_SHADER, v_src1, 1);

    f_src1 = "\n".join([
        "precision mediump float;",
        "varying vec4 vColor;",
        "void main()",
        "{",
        "   gl_FragColor = vColor;",
        "}"
    ]);
    f_shader = ShaderSrc(ShaderSrc.FRAGMENT_SHADER, f_src1, 1);

    shader_group = ShaderGroup(v_shader, f_shader)
    shader_group.attributes.append(("aPosition", "vec4"))
    shader_group.uniforms.append(("u_offsets", "vec4"))

    shader_info = {}
    shader_info[1] = [shader_group]
    shader_info[2] = [shader_group]

    if args.sp_file != None:
        shader_groups = extract_shaders_from_file(args.sp_file)

        import pdb
        pdb.set_trace()

        for sg in shader_groups:
            shader_info[1].append(sg)
            shader_info[2].append(sg)

    with open(args.output, "wb") as of:
        pickle.dump(shader_info, of)


if __name__ == '__main__':
    main()
