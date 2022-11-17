#include <regex>
#include <nlohmann/json.hpp>

#include "SVF-FE/LLVMUtil.h"
#include "SVF-FE/CPPUtil.h"

#include "Graphs/SVFG.h"
#include "WPA/Andersen.h"
#include "SVF-FE/SVFIRBuilder.h"
#include "Util/Options.h"

#include "util.h"

using namespace llvm;
using namespace std;
using namespace SVF;

struct APIInfo {
    string name;
    map<string, string> resolve;
};

// #define DBG 1

using json = nlohmann::json;

cl::OptionCategory cat("api_func_parse Options",
                       "These control the inputs to api_func_parse tool.");

static cl::opt<string> apispec("api_spec", cl::desc("Specify WebGL API spec file (json format)"),
                               cl::value_desc("apispec"), cl::Required, cl::cat(cat));

static cl::opt<string> ir("ir", cl::desc("Specify WebGL API IR file"),
                          cl::value_desc("IR file"), cl::Required, cl::cat(cat));

static cl::opt<string> dump_api("dump_api", cl::desc("dump all the functions parsed for it"),
                                cl::value_desc("api name"), cl::cat(cat));

static cl::opt<string> output("output", cl::desc("the file to dump the parsed result"),
                              cl::value_desc("json output file name"), cl::Required, cl::cat(cat));

bool parseApiArgTypes(string& raw, vector<string> &res) {
    auto lp1 = raw.find("(");
    auto lp2 = raw.rfind("(");
    auto rp1 = raw.rfind(")");
    auto rp2 = raw.find(")");

    res.clear();

    if (lp1 == string::npos || \
        rp1 == string::npos || \
        (lp1 != lp2) || (rp1 != rp2)) {
        return false;
    }
    auto s = lp1 + 1;
    auto e = rp1 - 1;
    int i;

    while (s < e) {
        int lb = 0;
        i = s;
        while (i < e) {
            if (raw[i] == '<') {
                lb ++;
            } else if (raw[i] == '>') {
                lb --;
            } else if (raw[i] == ',') {
                if (lb == 0) {
                    break;
                }
            }

            i++;
        }

        int l = i - s;
        if (i == e)
            l += 1;

        string t = trim(raw.substr(s, l));

        // 1. getBufferParameter
        // getProgramParameter etc
        // has an extra blink::ScriptState as the first argument
        // we ignore them

        // 2. makeXRCompatible
        // texImage2D etc
        // take an extra argument of type
        // blink::ExceptionState& (the last argument)
        // we remove it here

        // 3. texImagexD etc
        // take an extra argument of type
        // blink::ExecutionContext* (the first argument)
        // we remove it here

        if (0 != t.compare("blink::ScriptState*") &&
            0 != t.compare("blink::ExceptionState&") &&
            0 != t.compare("blink::ExecutionContext*"))
            res.push_back(t);

        s = i + 1;
    }

    return true;
}

static bool
match(struct cppUtil::DemangledName &dname, json &spec, int version) {
    string &rawName = dname.rawName;
    bool ret = true;
    vector<string> res;
    if (!parseApiArgTypes(rawName, res)) {
        cout << "failed to parse the arg types" << endl;
    }

    json &args = spec["args"];

    if (res.size() != args.size()) {
        ret = false;
    } else {
        for (int i = 0; i < args.size(); i ++) {

            string &farg = res[i];
            string sarg = args[i]["arg_type"].get<string>();

            // handle ArrayBufferView
            // and ArrayBuffer args
            auto pt = sarg.rfind("OrNull");
            if (pt != string::npos) {
                string t = sarg.substr(0, pt);
                if (farg.find(t) == string::npos) {
                    ret = false;
                    break;
                }

                // ArrayBuffer does not match ArrayBufferView
                auto vt = t.rfind("View");
                if (vt == string::npos && farg.find(t + "View") != string::npos) {
                    ret = false;
                    break;
                }
            }

            // handle GLsizexxptr
            if (sarg.find("GL") == 0 && sarg.rfind("ptr") != string::npos) {
                if (farg != "long") {
                    ret = false;
                    break;
                }
            }

            // handle ImageData
            if (sarg == "ImageData" && farg.find(sarg) == string::npos) {
                ret = false;
                break;
            }

            // handle texImagenD
            // HTMLImageElement
            // HTMLVideoElement
            if (sarg.find("HTML") == 0 && sarg.find("HTMLCanvas") == string::npos &&
                farg.find(sarg) == string::npos) {
                ret = false;
                break;
            }

            // Handle HTMLCanvasElement
            if (sarg == "HTMLCanvasElement" && farg.find("VideoFrame") == string::npos) {
                ret = false;
                break;
            }

            // Handle OffscreenCanvas
            if (sarg == "OffscreenCanvas" && farg.find("CanvasRenderingContextHost") == string::npos) {
                ret = false;
                break;
            }


            if (sarg == "ImageBitmap" && farg.find("ImageBitmap") == string::npos) {
                ret = false;
                break;
            }


            // handle array vs sequence
            if (sarg.find("Array") != string::npos && farg.find("Array") == string::npos) {
                ret = false;
                break;
            }

            // GLfloatSequence
            if (sarg.find("Sequence") != string::npos && farg.find("Vector") == string::npos) {
                ret = false;
                break;
            }
        }

        if (version == 1 && dname.className.find("WebGL2") != string::npos) {
            ret = false;
        }
    }

    return ret;
}

int main(int argc, char **argv) {
    cl::ParseCommandLineOptions(argc, argv,
                                "Analyzing the llvm functions of each WebGL API\n");

    ifstream i(apispec);
    json spec;

    if (!i) {
        cout << "api_spec file not accessible: " << apispec << endl;
        return -1;
    }

    i >> spec;

    int sver = spec["version"].get<int>();

    json &apis = spec["apis"];
    map<int, APIInfo> api_res;
    map<string, set<int>> name2ids;
    set<int> seenIds;

    for (int i = 0; i < apis.size(); i++) {
        json &api = apis[i];
        int id = api["id"].get<int>();
        string name = api["name"].get<string>();

        api_res[i] = {name, {}};

        name2ids[name].insert(id);
    }

    SVFModule* svfModule = LLVMModuleSet::getLLVMModuleSet()->buildSVFModule({ir});

    for (auto it = svfModule->llvmFunBegin(); it != svfModule->llvmFunEnd(); it ++) {
        // cout << (*it)->getName().str() << endl;
        string mname = (*it)->getName().str();
        auto dname = cppUtil::demangle(mname);
        if (dname.className.find("blink::WebGL") == 0) {

            if (dump_api != "" ) {
                static int i = 0;
                if ( dname.funcName == dump_api) {
                    cout << "i=" << i++ << endl;
                    cout << "oname:" << mname << endl;
                    cout << "className: " <<  dname.className << endl;
                    cout << "funcName: " << dname.funcName << endl;
                    cout << "dmangedName: " << dname.rawName << endl;
                    cout << "======================================\n";
                }
            } else {

                if (name2ids.find(dname.funcName) != name2ids.end()) {
                    for (auto &id : name2ids[dname.funcName]) {
                        seenIds.insert(id);

                        if (match(dname, apis[id], sver)) {

                            if (api_res[id].resolve.size() == 0) {
                                api_res[id].resolve[mname] = dname.rawName;
                                continue;
                            }

                            if (sver == 2 && dname.className.find("WebGL2") != string::npos) {
                                api_res[id].resolve.clear();
                                // overwrite
                                api_res[id].resolve[mname] = dname.rawName;
                            }
                        }
                    }
                }
            }

        }
    }

    if (dump_api != "") {
        return 0;
    }

    json o;
    o["version"] = sver;
    json m;

    for (int i = 0; i < apis.size(); i ++) {
        json mi;
        APIInfo &info = api_res[i];
        mi["id"] = i;
        mi["name"] = info.name;
        assert(info.resolve.size() == 1 && "name resolving failed");
        auto it = info.resolve.begin();
        mi["llvm_fname"] = it->first;
        mi["dm_name"] = it->second;

        m.push_back(mi);
    }

    o["mappings"] = m;

    string of;
    if (output == "") {
        of = "output.json";
    } else {
        of = output;
    }
    ofstream ofs(of);

    // write the result
    ofs << setw(4);
    ofs << o;

    return 0;
}
