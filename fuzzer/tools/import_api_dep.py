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

#!/usr/bin/env python3

import os
import sys
import networkx as nx
import json
import argparse
import pickle

graphml_filename = "dep_graph.graphml"
output_file = "apidep.pickle"

link_key = "__DEPS__"

class ApiNode:

    def __init__(self, _id, _name):
        self.id = _id
        self.name = _name

    def __str__(self):
        return "id:" + str(self.id) + "\n" + "name:" + self.name

class MsgNode:

    def __init__(self, msg, apiid):
        msg = msg.strip('\x00')
        self.msg = msg
        self.apiid =apiid

    def __str__(self):
        return "apiid:" + str(self.apiid) + "\n" + "msg:" + self.msg

def build_dep_graph(res):
    di_graph = nx.DiGraph()
    id2node = {}

    msgnode_dict = {}

    for api in res:
        _id = api["id"]
        _name = api["apiname"]
        apinode = ApiNode(_id, _name)
        id2node[_id] = apinode
        di_graph.add_node(apinode, color='red')

        if "msgs" not in api or api["msgs"] == None:
            print("apiname:", api["apiname"], ", id:", api["id"], "does not contain msgs field")
            continue

        for msg, deps in api["msgs"].items():
            msgnode = MsgNode(msg, _id)
            di_graph.add_node(msgnode, color='blue')
            # here we use the msg and the id of the api as key
            k = (msg, _id)
            msgnode_dict[k] = msgnode
            di_graph.add_edge(apinode, msgnode, color='red')

    # add the dep edges
    for api in res:
        _id = api["id"]
        _name = api["apiname"]

        if "msgs" not in api or api["msgs"] == None:
            print("apiname:", api["apiname"], ", id:", api["id"], "does not contain msgs field")
            continue

        for msg in api["msgs"].keys():
            d_dep = api["msgs"][msg][link_key]

            if d_dep == None or len(d_dep) == 0:
                print("No dep found for ({apiname}, {msg})".format(apiname=_name, msg=msg))
                continue
            
            for aid in d_dep:
                apinode = id2node[aid]
                k = (msg, _id)
                msgnode = msgnode_dict[k]
                di_graph.add_edge(msgnode, apinode, color='blue')

                print(">>>>> api dep: ({fapi}, {fid}, {msg}) -> ({tname}, {tid})".format(fapi=_name,
                                                                                         fid=_id,
                                                                                         msg=msg,
                                                                                         tname=apinode.name,
                                                                                         tid=apinode.id))

    nx.write_graphml(di_graph, graphml_filename)

def resolve_dependency(res, update_dict):

    for api in res:
        # compute the deps
        # merging all the deps from all sets
        print("apiname:", api["apiname"], ", id:", api["id"])

        if "msgs" not in api or api["msgs"] == None:
            print("apiname:", api["apiname"], ", id:", api["id"], "does not contain msgs field")
            continue

        for msg, deps in api["msgs"].items():

            d_deps = set()
            # import pdb
            # pdb.set_trace()
            print("-- msg:", msg)
            for ds, fields in deps.items():
                if ds not in update_dict:
                    continue
                d = update_dict[ds]

                for field in fields:
                    if field not in d:
                        continue
                    # print("d[field]", d[field])
                    # for e in d[field]:
                    #    deps.add(e)
                    d_deps.update(d[field])

            deps[link_key] = d_deps

def preparse_updates(res_json_file):
    with open(res_json_file) as inf:
        res = json.load(inf)

    # data structure -> { field -> {api0, api1, ...}  }
    update_dict = {}

    # iterate through all the apis
    for api in res:

        if "updates" not in api:
            print("`updates` field not presented in api")
            continue

        for ds, fields in api["updates"].items():

            if ds not in update_dict:
                update_dict[ds] = {}

            d = update_dict[ds]
            for field in fields:
                if field not in d:
                    d[field] = set()

                s = d[field]
                s.add(api["id"])

    # return the results
    return res, update_dict

def gen_pickle(res):
    # p_res : apiid -> {msg -> [dep api ids]}
    p_res = {}

    for api in res:
        if "msgs" in api and api["msgs"] != None:
            _id = api["id"]
            dep = {}
            for msg in api["msgs"].keys():
                # TODO: there might be some inconsistencies between the messages
                # we have here and the messages we get from the browser at fuzzing time
                s_msg = msg.strip('\x00')
                dep[s_msg] = api["msgs"][msg][link_key]

            p_res[_id] = dep

    with open(output_file, "wb") as outf:
        pickle.dump(p_res, outf)

def main():
    parser = argparse.ArgumentParser(prog="import_api_dep",
                                     description="a tool for parsing" +
                                     " the dependecies among apis")

    parser.add_argument("--dep_res", required=True,
                        help="a json file with the result" +
                        " dumped by the static analyzer")
    parser.add_argument("--output", required=False,
                        help="a file to write the result")


    parser.add_argument("--graphml", required=False,
                        help="a file to write the graph ml result")

    args = parser.parse_args()

    dep_res = args.dep_res
    if not os.path.exists(dep_res):
        print("dependency result file not exists")
        sys.exit(-1)

    if args.graphml != None:
        graphml_filename = args.graphml

    if args.output != None:
        output_file = args.output

    # start parsing the results
    res, update_dict = preparse_updates(dep_res)
    resolve_dependency(res, update_dict)

    # building graph file
    build_dep_graph(res)
    # generate the pickle file
    gen_pickle(res)

if __name__ == '__main__':
    main()
