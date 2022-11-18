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


import os
from yapf.yapflib.yapf_api import FormatCode
from program.api_spec import WebGLSpecs
from enum import Enum
import re
import nltk
import json
import stringcase

class mutate(Enum):
    INCREASE_ARG = 1
    DECREASE_ARG = 2
    TYPE_ERROR = 3
    RANDOM_ARG = 0

class gltype(Enum):
    INT = 1  # GLsizei, GLuint, GLint
    FLOAT = 2
    BOOL = 3
    PTR = 4
    VOID = 5

def __load_log_messages_from(log_msg_file):

    ret = []

    if os.path.exists(log_msg_file):
        with open(log_msg_file) as f:
            data = f.read()
            ret += eval(data)
    else:
        print("{log_msg_file} does not exist".format(log_msg_file=
                                                     log_msg_file))

    return ret

def load_log_messages(file_name):
    __cur_dir = os.path.dirname(__file__)

    ret = []

    blink_webgl_log_stmts_file = os.path.join(__cur_dir, file_name)
    ret += __load_log_messages_from(blink_webgl_log_stmts_file)

    return ret

def get_text_in_parentheses(s):
    re_parentheses = re.compile(r"\((.*)\)")
    return re_parentheses.search(s).group(0)[1:-1]

class culprit_tree:
    stopwords = [
        "can", "cannot", "could", "couldn't", "shall", "should", "shouldn't",
        "may", "might", "will", "would", "won't", "wouldn't", "ought",
        "failure", "attempt", "create"
    ]

    def __init__(self, tree):
        if isinstance(tree, nltk.tree.Tree):
            # _ref_tree is the parsed tree for the whole message
            self._ref_tree = tree
            print(tree)
        else:
            print("ERROR: create culprit tree from non-tree object")
        self._culprits = culprit_tree._find_culprit(self)

    def get_culprits(self):
        return self._culprits

    def _find_culprit(self):
        culprits = []

        for st in self._ref_tree.subtrees():
            if st.label() == "NP":
                culprits_name = " ".join([elem[0] for elem in st.leaves() \
                 if elem[1] in ["NN", "NNP", "NNS"] and elem[0] not in culprit_tree.stopwords])
                if len(culprits_name) > 0:
                    culprits.append(culprits_name)
        return culprits


class gl_error_log_entry:
    def __init__(self, log):
        log_args = get_text_in_parentheses(log).split(",")

        self.log_entry = log
        self.log_type = log_args[0].strip()
        self.api = log_args[1].strip()
        self.message = log_args[2].strip(" .\n\t").lower()

    def get_log_entry(self):
        return self.log_entry

    def get_log_type(self):
        return self.log_type

    def get_api(self):
        if self.api.startswith("gl"):
            return self.api[2:]
        return self.api

    def is_internal(self):
        if self.api.endswith("INTERNAL"):
            return True
        if self.api.endswith("CHROMIUM"):
            return True
        return False

    def get_message(self):
        return self.message

    def get_tokens(self):
        return nltk.pos_tag(self.message.split())

    def get_np_tree(self):
        grammar = r"""
			NP: {<DT>?<JJ>*<NNP>*<NN>*<NNS>*<NN|NNP|NNS>}
		"""

        cp = nltk.RegexpParser(grammar)
        tree = cp.parse(self.get_tokens())

        return tree

    def get_rel_tree(self):
        over = ["out of", ">", "overflow", "large", "big", "above", "decrease"]

        under = ["<", "underflow", "small", "below", "increase"]

        compatible = ".*(valid|compatible).*type"
        compatible_rev = ".*type.*(valid|compatible)"

        if any(i in self.get_message() for i in over):
            return mutate.DECREASE_ARG
        elif any(i in self.get_message() for i in under):
            return mutate.INCREASE_ARG
        elif re.match(compatible, self.get_message()) or \
         re.match(compatible_rev, self.get_message()):
            return mutate.TYPE_ERROR
        else:
            return mutate.RANDOM_ARG

class CodeGenerator:
    def __init__(self, indentation='\t'):
        self.indentation = indentation
        self.level = 0
        self.code = ''

    def indent(self):
        self.level += 1

    def dedent(self):
        if self.level > 0:
            self.level -= 1

    def __add__(self, value):
        self.code = str(self) + ''.join(
            [self.indentation
             for i in range(0, self.level)]) + str(value) + '\n'
        return self

    def __str__(self):
        return str(self.code)


def change_string_style(s):
    result = ""
    for i in range(0, len(s)):
        if s[i].isupper():
            if i == 0:
                result += s[i].lower()
            else:
                result += "_" + s[i].lower()
        else:
            result += s[i]
    return result

def format_keywords(s):
    regex = re.compile('[^a-zA-Z]')
    s = regex.sub('', s)
    return stringcase.pascalcase(s)


def lower_first_char(s):
    return s[0].lower() + s[1:]

class MutatorGenerator(CodeGenerator):
    def __init__(self, mutator_identifier):
        super().__init__()
        self.mutator_identifier = mutator_identifier
        self.message = ""

        self += "from ..base_mutator import BaseMutator"
        self += "import random"
        self += ""

    def set_multiple_apis(self, apis):
        self += "_api_names=\"" + ",".join(
            [lower_first_char(api) for api in apis]) + "\""
        self += ""

    def set_single_api(self, api):
        self += "_api_names=\"" + api + "\""
        self += ""

    def set_message(self, msg):
        self.message = msg
        self += "def " + change_string_style(self.mutator_identifier) + \
            "_mutator_match(program, api, log_message, **kwargs):"
        self.indent()
        self += "return \"" + msg + "\" in (log_message.message.lower() if log_message.message is not None else \"\")"
        self += ""
        self.dedent()

    def set_mutation(self, api):
        mutator_identifier = self.mutator_identifier
        self += "class " + mutator_identifier + "Mutator(BaseMutator):"
        self.indent()

        self += ""
        self += "def __init__(self):"
        self.indent()
        self += "self.name = \"" + mutator_identifier + "Mutator\""
        self += ""
        self.dedent()
        self += "def _mutate(self, program, api, **kwargs):"
        self.indent()
        self += "program.gen_args_for_api_and_add_to_program_by_name(\"" + api.name + "\")"
        self += "print(\"" + mutator_identifier + "\")"
        self += "return True"
        self.dedent()
        self.dedent()

    def set_data_mutation(self, api, arg, rel):
        mutator_identifier = self.mutator_identifier
        values = []
        constraints = []
        self += "class " + mutator_identifier + "Mutator(BaseMutator):"
        self.indent()
        self += ""
        self += "def __init__(self):"
        self.indent()
        self += "self.name = \"" + mutator_identifier + "Mutator\""
        self += ""
        self.dedent()
        self += "def _mutate(self, program, api, **kwargs):"
        self.indent()

        arg_index = api.args.index(arg) if arg in api.args else -1

        self += "api.set_arg_val({0}, api.args[{0}].arg_type.gen_value(None, api, api.args[{0}]))".\
            format(arg_index)

        self += "print(\"" + mutator_identifier + "\")"
        self += "return True"
        self.dedent()
        self.dedent()

# adapted from https://stackoverflow.com/questions/18715688/find-common-substring-between-two-strings
def longest_substring(string1, string2):
    answer = ""
    len1, len2 = len(string1), len(string2)
    for i in range(len1):
        for j in range(len2):
            lcs_temp=0
            match=''
            while ((i+lcs_temp < len1) and (j+lcs_temp<len2) and string1[i+lcs_temp] == string2[j+lcs_temp]):
                match += string2[j+lcs_temp]
                lcs_temp+=1
            if (len(match) > len(answer)):
                answer = match
    return answer

def get_api_by_name(specs, api_name):
    api_name = api_name.lower()

    for api in specs[1].apis + specs[2].apis:
        if api.name.lower() == api_name:
            return api

    return None

STATS_EXACT_MATCH = 0
STATS_TOTAL_MATCH = 0
STATS_IS_EXACT_MATCH = False
STATS_EXACT_MATCH_PER_API = 0
STATS_TOTAL_MATCH_PER_API = 0
STATS_LONGEST_SUBSTR = 0
STATS_DEPENDENCY_MUTATE = 0
STATS_TOTAL_MUTATE = 0

def find_argument_order(specs, api_name, arg):
    global STATS_TOTAL_MATCH, \
    STATS_EXACT_MATCH, \
    STATS_DEPENDENCY_MUTATE, \
    STATS_LONGEST_SUBSTR, \
    STATS_TOTAL_MUTATE, \
    STATS_EXACT_MATCH_PER_API, \
    STATS_TOTAL_MATCH_PER_API, \
    STATS_IS_EXACT_MATCH

    api_name = api_name.lower()
    arg = arg.lower()
    api_spec = None
    longest_match_api = [0, None]

    for api in specs[1].apis + specs[2].apis:
        if api.name.lower() == api_name:
            api_spec = api
            break

    if api_spec == None:
        return None

    STATS_TOTAL_MATCH += 1
    STATS_IS_EXACT_MATCH = False

    for api_arg in api_spec.args:
        if arg in api_arg.name:
            STATS_EXACT_MATCH += 1
            STATS_IS_EXACT_MATCH = True
            return api_arg

    for api_arg in api_spec.args:
        common_substring = longest_substring(arg, api_arg.name)
        if len(common_substring) > longest_match_api[0]:
            longest_match_api[1] = api_arg
            longest_match_api[0] = len(common_substring)
            STATS_LONGEST_SUBSTR += len(common_substring)

    return longest_match_api[1]

def gen_mutator_files(mutations):
    global STATS_TOTAL_MATCH, \
    STATS_EXACT_MATCH, \
    STATS_LONGEST_SUBSTR, \
    STATS_DEPENDENCY_MUTATE, \
    STATS_TOTAL_MUTATE

    for k in mutations.keys():
        mutator_id = format_keywords(k[0] + k[1])
        cg = MutatorGenerator(mutator_id)
        cg.set_single_api(k[1])
        cg.set_message(k[0])

        STATS_TOTAL_MUTATE += 1
        if (k[1] == mutations[k][0].name):
            cg.set_data_mutation(mutations[k][0], mutations[k][1], mutations[k][2])
        else:
            STATS_DEPENDENCY_MUTATE += 1
            cg.set_mutation(mutations[k][0])

        print(">>" * 40)
        print(cg)
        print("<<" * 40)

        filename = change_string_style(mutator_id) + "_mutator.py"
        file = open("gen/" + filename, "w")
        formatted_cg = FormatCode(str(cg))
        file.write(formatted_cg[0])
        file.close()

def main():
    global STATS_EXACT_MATCH_PER_API, STATS_TOTAL_MATCH_PER_API, STATS_IS_EXACT_MATCH

    mutations = {}

    err_msgs = load_log_messages("blink_errors.dat")

    for i in err_msgs:
        entry = gl_error_log_entry(i)

        if entry.is_internal():
            continue

        if "name" in entry.get_api():
            continue

        if entry.get_api().startswith("Do"):
            continue

        print("\n\n" + entry.get_api())

        print(entry.get_message())

        print(entry.get_log_type())

        ct = culprit_tree(entry.get_np_tree())
        rel = entry.get_rel_tree()
        print(rel)

        if entry.get_log_type() in [
            "GL_INVALID_VALUE", "GL_INVALID_OPERATION"]:
            print(ct.get_culprits())
            for c in ct.get_culprits():
                    arg = find_argument_order(WebGLSpecs,
                                            entry.get_api(),
                                            c)

                    if STATS_IS_EXACT_MATCH:
                        STATS_EXACT_MATCH_PER_API += 1

                    STATS_TOTAL_MATCH_PER_API += 1

                    if arg == None:
                        continue

                    if len(arg.depends_on) > 0:
                        mutations[(c, entry.get_api())] = \
                            [get_api_by_name(WebGLSpecs, arg.depends_on[0]), arg, rel]
                    else:
                        mutations[(c, entry.get_api())] = \
                            [get_api_by_name(WebGLSpecs, entry.get_api()), arg, rel]

                    print(c, entry.get_api(), "->", 
                        get_api_by_name(WebGLSpecs, entry.get_api()), arg, rel)
            print("")

    gen_mutator_files(mutations)

if __name__ == "__main__":
    main()
    print("Exactly matched arguments (# of culprits):", STATS_EXACT_MATCH / STATS_TOTAL_MATCH)
    print("Exactly matched arguments (# of API):", STATS_EXACT_MATCH_PER_API / STATS_TOTAL_MATCH_PER_API)
    print("Average longest substring match:", STATS_LONGEST_SUBSTR / (STATS_TOTAL_MATCH - STATS_EXACT_MATCH))
    print("Dependency mutation:", STATS_DEPENDENCY_MUTATE / STATS_TOTAL_MUTATE)
