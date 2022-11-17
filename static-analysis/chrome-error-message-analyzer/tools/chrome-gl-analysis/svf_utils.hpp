#ifndef SVF_UTILS_H_
#define SVF_UTILS_H_

#include <iostream>
#include <string>

#include "Graphs/VFG.h"
#include "Graphs/SVFG.h"
#include "SVF-FE/SVFIRBuilder.h"
#include "Graphs/ICFG.h"
#include "Util/WorkList.h"

using namespace SVF;
using namespace std;
using namespace llvm;

const SVFFunction *getFunctionByName(SVFModule *mod, const string &name);

// this function tranverse the ICFG from the entry
// of a given function name and calls a visitor
// for each instruction
// ICFG is considered to have handled all indirect calls
template <class InstVisitorClass>
void traverseFunctionICFG(ICFG *icfg,
                          const SVFFunction *svfFun,
                          InstVisitorClass &visitor) {

    Function *llvmFun = svfFun->getLLVMFun();

    BasicBlock *entryBlock = &llvmFun->getEntryBlock();

    Instruction *inst = &entryBlock->front();

    ICFGNode *iNode = icfg->getICFGNode(inst);
    FIFOWorkList<const ICFGNode *> worklist;
    Set<const ICFGNode *> visited;

    worklist.push(iNode);

    while (!worklist.empty()) {
        const ICFGNode *vNode = worklist.pop();
        visited.insert(vNode);

        // which icfg nodes do we want to visit?
        // we can add code here
        if (const auto *cbnode = llvm::dyn_cast<CallICFGNode>(vNode)) {
            const Instruction *inst = cbnode->getCallSite();
            visitor.visit(const_cast<Instruction *>(inst));
        } else if (const auto *inode = llvm::dyn_cast<IntraICFGNode>(vNode)) {
            const Instruction *inst = inode->getInst();
            visitor.visit(const_cast<Instruction *>(inst));
        }

        for (auto it = vNode->OutEdgeBegin(), eit = vNode->OutEdgeEnd();
             it != eit; ++it) {

            ICFGEdge *edge = *it;

            // skip ret edge
            if (edge->isRetCFGEdge())
                continue;

            ICFGNode *succNode = edge->getDstNode();
            if (visited.find(succNode) == visited.end()) {
                worklist.push(succNode);
            }
        }
    }
}

vector<const Instruction*>
computeConditions(ICFG *icfg, const Instruction *inst);

bool is_webgl_internal_value(const llvm::Value *v);

set<const Instruction *>
collectErrEmittingInsts(ICFG *icfg,
                        string &eef_name,
                        const SVFFunction *svfFun);

set<const Value *>
computeUpdatedInternalVars(ICFG *icfg,
                           const SVFFunction *svfFun);

set<int>
computeTargetArgs(VFG *vfg,
               const Value *val,
               const Function *func);

map<string, set<int>>
summarizeFieldAccessInfo(set<const llvm::Value *> &raw_values);

set<const Value *>
computeInternalTaintSrcs(VFG *vfg, const Value *val);
#endif // SVF_UTILS_H_
