#include <set>
#include <vector>

#include "Util/BasicTypes.h"

#if LLVM_VERSION_MAJOR > 10
#include <llvm/IR/AbstractCallSite.h>
#endif

#include <llvm/IR/InstVisitor.h>

#include "svf_utils.hpp"
#include "llvm_utils.hpp"

using namespace SVF;
using namespace std;
using namespace llvm;

const SVFFunction *getFunctionByName(SVFModule *mod, const string &name) {

    for (const auto *fun : *mod) {
        Function *llvmFun = fun->getLLVMFun();
        if (llvmFun->getName().str() == name) {
            return fun;
        }
    }
    return nullptr;
}

// this function finds the conditions
// of instruction in the same function
// Note: this function may be simplified
// with cinditionVal in IntraCFGEdge
//
// This tranversal is constrained in on function
//
// TODO: handle case where a validate function is used
// XXX
vector<const Instruction*>
computeConditions(ICFG *icfg,
                  const Instruction *inst) {
    vector<const Instruction *> ret;
    set<const ICFGNode *> visited;

    assert(icfg && "ICFG passed in is nullptr");
    assert(inst && "inst passed in is nullptr");

    FIFOWorkList<const ICFGNode *> worklist;
    ICFGNode *from = icfg->getICFGNode(inst);

    assert(from && "Could not find the ICFGNode");

    worklist.push(from);

    while (!worklist.empty()) {
        const ICFGNode *vNode = worklist.pop();
        visited.insert(vNode);

        if (const auto *inode = llvm::dyn_cast<IntraICFGNode>(vNode)) {
            const Instruction *inst = inode->getInst();

            if (auto *_br_inst = llvm::dyn_cast<llvm::BranchInst>(inst)) {
                ret.push_back(_br_inst);
            } else if (auto *_sw_inst = llvm::dyn_cast<llvm::SwitchInst>(inst)) {
                ret.push_back(_sw_inst);
            }
        }

        for (auto it = vNode->InEdgeBegin(), eit = vNode->InEdgeEnd();it != eit; ++it) {
            ICFGEdge *edge = *it;

            if (!edge->isIntraCFGEdge()) {
                continue;
            }

            const ICFGNode* sNode = edge->getSrcNode();

            if (visited.count(sNode) == 0) {
                worklist.push(sNode);
            }

        }
    }

    return ret;
}

bool is_webgl_internal_value(const llvm::Value *v) {

    if (llvm::isa<llvm::AllocaInst>(v)) {
        return false;
    } else {
        if (llvm::isa<llvm::GetElementPtrInst>(v)) {
            const auto *gep =
                llvm::dyn_cast<const llvm::GetElementPtrInst>(v);

            llvm::Type *t = gep->getSourceElementType();
            if (!t->isStructTy()) {
                return false;
            }

            const string &struct_name = t->getStructName().str();

            if (struct_name.find("class.blink::") == string::npos &&
                struct_name.find("struct.blink::") == string::npos) {
                return false;
            }

            if (struct_name == "class.blink::HeapObjectHeader" ||
                struct_name == "class.blink::NormalPageArena" ||
                struct_name == "class.blink::WebGLFastCallHelper") {
                return false;
            }

            return true;
        }
    }

    return false;
}

class CallToFuncVisitor : public InstVisitor<CallToFuncVisitor> {
    private:
        string &_fname;
        set<const Instruction *> _res;

    public:
        CallToFuncVisitor(string &fname)
            : _fname(fname) {}

        void visitCallInst(CallInst &callInst) {

#if LLVM_VERSION_MAJOR < 11
            ImmutableCallSite cs(&callInst);
            if (const auto *f = cs.getCalledFunction()) {
                if (f->getName().str() == _fname) {
                    _res.insert(cs.getInstruction());
                }
            }
#else
            AbstractCallSite cs(&callInst.getCalledOperandUse());
            if (cs.isDirectCall()) {
                if (const auto *f = cs.getCalledFunction()) {
                    if (f->getName().str() == _fname) {
                        _res.insert(cs.getInstruction());
                    }
                }
            }
#endif
        }

        set<const Instruction *> &getRes() {
            return _res;
        }
};

set<const Instruction *>
collectErrEmittingInsts(ICFG *icfg,
                        string &eef_name,
                        const SVFFunction *svfFun) {

    CallToFuncVisitor cfVisitor(eef_name);
    traverseFunctionICFG(icfg, svfFun, cfVisitor);

    return cfVisitor.getRes();
}

class UpdateVarVisitor : public InstVisitor<UpdateVarVisitor> {
    private:
        set<const Value *> _res;

    public:
        void visitStoreInst(StoreInst &storeInst) {
            auto *v = storeInst.getPointerOperand();
            if (is_webgl_internal_value(v)) {
                _res.insert(v);
            }
        }

        set<const Value*> &getRes() {
            return _res;
        }
};

set<const Value *>
computeUpdatedInternalVars(ICFG *icfg,
                           const SVFFunction *svfFun) {
    UpdateVarVisitor vvv;
    traverseFunctionICFG(icfg, svfFun, vvv);

    return vvv.getRes();
}

set<int>
computeTargetArgs(VFG *vfg,
               const Value *val,
               const Function *func) {
    set<int> res;

    auto *pag = SVFIR::getPAG();

    PAGNode *pNode = pag->getGNode(pag->getValueNode(val));
    const VFGNode *vNode = vfg->getDefVFGNode(pNode);
    FIFOWorkList<const VFGNode *> worklist;
    Set<const VFGNode *> visited;
    worklist.push(vNode);

    while (!worklist.empty()) {
        const VFGNode *vNode = worklist.pop();
        visited.insert(vNode);

        if (const auto *parmVFGNode = SVFUtil::dyn_cast<FormalParmVFGNode>(vNode)) {
            const PAGNode *param = parmVFGNode->getParam();
            const Function *containingFunc = param->getFunction();

            if (containingFunc != func) {
                continue;
            }

            const Value *llvmValue = param->getValue();
            if (const auto *arg = SVFUtil::dyn_cast<Argument>(llvmValue)) {
                res.insert(arg->getArgNo());
            }
        }
        for (auto it = vNode->InEdgeBegin(),
                 eit = vNode->InEdgeEnd();
             it != eit; ++it) {
            VFGEdge *edge = *it;
            VFGNode *prev = edge->getSrcNode();
            if (visited.find(prev) == visited.end()) {
                worklist.push(prev);
            }
        }
    }

    return res;
}

static bool filterout_data_structure(const string &struct_name) {
  if (struct_name.find("class.blink::") == 0 ||
      struct_name.find("struct.blink::")) {
    return false;
  }

  return true;
}

// given a set of values
// we analyze it and return a map
// the key is the data structure
// and value is a set of indices
// which reprents which fields the code accesses
map<string, set<int>>
summarizeFieldAccessInfo(set<const llvm::Value *> &raw_values) {
  map<string, set<int>> res;

  for (const auto &v:raw_values) {
    if (const auto* gep = llvm::dyn_cast<llvm::GetElementPtrInst>(v)) {
      llvm::Type *source_type = gep->getSourceElementType();
      if (source_type->isStructTy()) {
        const string& tname = source_type->getStructName().str();
        // Here the first one is ignored for the moment
        // the first operand is the pointer
        // the second one typically zero
        // and the third one is the index into the data structure
        // TODO: more analysis on all the GEP instructions
        for (unsigned int i = 2; i < gep->getNumOperands(); i++) {

            // we only look at constant indices
            // variable indices are ignored for the moment
            // we assume that variable indices are mainly used for
            // Array access
            // while constant indices are for accessing elements
            // of structure and classes.
            if (auto *ci = llvm::dyn_cast<llvm::ConstantInt>(gep->getOperand(i))) {
                auto int_v = ci->getZExtValue();
                res[tname].insert(int_v);
            }
        }
      }
    }
  }
  return res;
}

set<const Value *>
computeInternalTaintSrcs(VFG *vfg, const Value *val) {
    set<const Value *> res;

    auto *pag = SVFIR::getPAG();
    PAGNode *pNode = pag->getGNode(pag->getValueNode(val));
    const VFGNode *vNode = vfg->getDefVFGNode(pNode);
    FIFOWorkList<const VFGNode *> worklist;
    Set<const VFGNode *> visited;
    worklist.push(vNode);


    while (!worklist.empty()) {
        const VFGNode *vNode = worklist.pop();
        visited.insert(vNode);

        if (const auto *loadVFGNode = SVFUtil::dyn_cast<LoadVFGNode>(vNode)) {
            const Instruction *i = loadVFGNode->getInst();
            if (auto *loadInst = llvm::dyn_cast<LoadInst>(i)) {
                const Value *v = loadInst->getPointerOperand();
                if (is_webgl_internal_value(v)) {
                    res.insert(v);
                }
            }
        }

        for (auto it = vNode->InEdgeBegin(),
                 eit = vNode->InEdgeEnd();
             it != eit; ++it) {
            VFGEdge *edge = *it;
            VFGNode *prev = edge->getSrcNode();
            if (visited.find(prev) == visited.end()) {
                worklist.push(prev);
            }
        }
    }

    return res;
}
