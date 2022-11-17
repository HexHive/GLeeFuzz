//===- BasicTypes.h -- Basic types used in SVF-------------------------------//
//
//                     SVF: Static Value-Flow Analysis
//
// Copyright (C) <2013-2017>  <Yulei Sui>
//

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
//===----------------------------------------------------------------------===//

/*
 * BasicTypes.h
 *
 *  Created on: Apr 1, 2014
 *      Author: Yulei Sui
 */

#ifndef BASICTYPES_H_
#define BASICTYPES_H_

#include "Util/SVFBasicTypes.h"
#include "Graphs/GraphPrinter.h"
#include "Util/Casting.h"
#include <llvm/ADT/SparseBitVector.h>
#include <llvm/IR/Instructions.h>
#include <llvm/IR/InstVisitor.h>	// for instruction visitor
#include <llvm/IR/InstIterator.h>	// for inst iteration
#include <llvm/IR/GetElementPtrTypeIterator.h>	//for gep iterator
#include <llvm/ADT/StringExtras.h>	// for utostr_32
#include <llvm/Analysis/AliasAnalysis.h>
#include <llvm/Analysis/CallGraph.h>	// call graph
#include <llvm/IR/GlobalVariable.h>	// for GlobalVariable

#include <llvm/Bitcode/BitcodeWriter.h>		// for WriteBitcodeToFile
#include <llvm/Bitcode/BitcodeReader.h>     /// for isBitcode
#include <llvm/IRReader/IRReader.h>	// IR reader for bit file
#include <llvm/Analysis/DominanceFrontier.h>
#include <llvm/Analysis/PostDominators.h>
#include <llvm/ADT/GraphTraits.h>		// for Graphtraits
#include <llvm/Transforms/Utils/Local.h>	// for FindDbgAddrUses

#if (LLVM_VERSION_MAJOR >= 14)
#include <llvm/BinaryFormat/Dwarf.h>
#endif

#include "llvm/IR/CFG.h"
#include "llvm/BinaryFormat/Dwarf.h"

namespace SVF
{

class BddCond;


/// LLVM Basic classes
typedef llvm::Type Type;
typedef llvm::Function Function;
typedef llvm::BasicBlock BasicBlock;
typedef llvm::Value Value;
typedef llvm::Instruction Instruction;
typedef llvm::CallBase CallBase;
typedef llvm::GlobalValue GlobalValue;
typedef llvm::GlobalVariable GlobalVariable;

/// LLVM outputs
typedef llvm::raw_string_ostream raw_string_ostream;
typedef llvm::raw_fd_ostream raw_fd_ostream;

/// LLVM types
typedef llvm::StructType StructType;
typedef llvm::ArrayType ArrayType;
typedef llvm::PointerType PointerType;
typedef llvm::FunctionType FunctionType;

/// LLVM Aliases and constants
typedef llvm::Argument Argument;
typedef llvm::ConstantInt ConstantInt;
typedef llvm::ConstantPointerNull ConstantPointerNull;
typedef llvm::GlobalAlias GlobalAlias;

/// LLVM metadata
typedef llvm::NamedMDNode NamedMDNode;
typedef llvm::MDNode MDNode;

/// LLVM Instructions
typedef llvm::CallInst CallInst;
typedef llvm::StoreInst StoreInst;
typedef llvm::LoadInst LoadInst;


/// LLVM Iterators
#if LLVM_VERSION_MAJOR >= 11
typedef llvm::const_succ_iterator succ_const_iterator;
#else
typedef llvm::succ_const_iterator succ_const_iterator;
#endif
typedef llvm::GraphPrinter GraphPrinter;
typedef llvm::IntegerType IntegerType;

// LLVM Debug Information
typedef llvm::DISubprogram DISubprogram;

class SVFFunction : public SVFValue
{
private:
    bool isDecl;
    bool isIntri;
    Function* fun;
    BasicBlock* exitBB;
    std::vector<const BasicBlock*> reachableBBs;
    bool isUncalled;
    bool isNotRet;
    Map<const BasicBlock*,Set<const BasicBlock*>> dtBBsMap;
    Map<const BasicBlock*,Set<const BasicBlock*>> dfBBsMap;
    Map<const BasicBlock*,Set<const BasicBlock*>> pdtBBsMap;
    Map<const BasicBlock*,std::vector<const BasicBlock*>> bb2LoopMap;
public:

    SVFFunction(Function* f): SVFValue(f->getName().str(),SVFValue::SVFFunc),
        isDecl(f->isDeclaration()), isIntri(f->isIntrinsic()), fun(f), exitBB(nullptr), isUncalled(false), isNotRet(false)
    {
    }

    SVFFunction(Function* f, BasicBlock* exitBB, std::vector<const BasicBlock*> reachableBBs): SVFValue(f->getName().str(),SVFValue::SVFFunc),
        isDecl(f->isDeclaration()), isIntri(f->isIntrinsic()), fun(f), exitBB(exitBB), reachableBBs(reachableBBs), isUncalled(false), isNotRet(false)
    {
    }

    inline Function* getLLVMFun() const
    {
        assert(fun && "no LLVM Function found!");
        return fun;
    }

    inline bool isDeclaration() const
    {
        return isDecl;
    }

    inline bool isIntrinsic() const
    {
        return isIntri;
    }

    inline u32_t arg_size() const
    {
        return getLLVMFun()->arg_size();
    }

    const Value* getArg(u32_t idx) const
    {
        return getLLVMFun()->getArg(idx);
    }

    inline bool isVarArg() const
    {
        return getLLVMFun()->isVarArg();
    }

    inline const std::vector<const BasicBlock*>& getReachableBBs() const
    {
        return reachableBBs;
    }

    inline const bool isUncalledFunction() const
    {
        return isUncalled;
    }

    inline const void setIsUncalledFunction(const bool isUncalledFunction)
    {
        this->isUncalled = isUncalledFunction;
    }

    inline const void setIsNotRet(const bool doesNotRet)
    {
        this->isNotRet = doesNotRet;
    }

    inline const void setExitBB(BasicBlock* exitBB)
    {
        this->exitBB = exitBB;
    }

    inline const void setReachableBBs(std::vector<const BasicBlock*> reachableBBs)
    {
        this->reachableBBs = reachableBBs;
    }

    inline const Map<const BasicBlock*,Set<const BasicBlock*>>& getDomFrontierMap() const
    {
        return dfBBsMap;
    }

    inline Map<const BasicBlock*,Set<const BasicBlock*>>& getDomFrontierMap()
    {
        return dfBBsMap;
    }

    inline bool hasLoopInfo(const BasicBlock* bb) const
    {
        return bb2LoopMap.find(bb)!=bb2LoopMap.end();
    }

    inline const std::vector<const BasicBlock*>& getLoopInfo(const BasicBlock* bb) const
    {
        Map<const BasicBlock*, std::vector<const BasicBlock*>>::const_iterator mapIter = bb2LoopMap.find(bb);
        if(mapIter != bb2LoopMap.end())
            return mapIter->second;
        else
        {
            assert(hasLoopInfo(bb) && "loopinfo does not exit(bb not in a loop)");
            abort();
        }
    }

    inline void addToBB2LoopMap(const BasicBlock* bb, const BasicBlock* loopBB)
    {
        bb2LoopMap[bb].push_back(loopBB);
    }

    inline const Map<const BasicBlock*,Set<const BasicBlock*>>& getPostDomTreeMap() const
    {
        return pdtBBsMap;
    }

    inline Map<const BasicBlock*,Set<const BasicBlock*>>& getPostDomTreeMap()
    {
        return pdtBBsMap;
    }

    inline Map<const BasicBlock*,Set<const BasicBlock*>>& getDomTreeMap()
    {
        return dtBBsMap;
    }

    inline const Map<const BasicBlock*,Set<const BasicBlock*>>& getDomTreeMap() const
    {
        return dtBBsMap;
    }

    inline bool isUnreachable(const BasicBlock* bb) const
    {
        return std::find(reachableBBs.begin(), reachableBBs.end(), bb)==reachableBBs.end();
    }

    inline bool isNotRetFunction() const
    {
        return isNotRet;
    }

    inline const BasicBlock* getExitBB() const
    {
        return this->exitBB;
    }

    void getExitBlocksOfLoop(const BasicBlock* bb, Set<const BasicBlock*>& exitbbs) const
    {
        if (hasLoopInfo(bb))
        {
            const std::vector<const BasicBlock*>& blocks = getLoopInfo(bb);
            assert(!blocks.empty() && "no available loop info?");
            for (const BasicBlock* block : blocks)
            {
                for (succ_const_iterator succIt = succ_begin(block); succIt != succ_end(block); succIt++)
                {
                    const BasicBlock* succ = *succIt;
                    if ((std::find(blocks.begin(), blocks.end(), succ)==blocks.end()))
                        exitbbs.insert(succ);
                }
            }
        }
    }

    bool isLoopHeader(const BasicBlock* bb) const
    {
        if (hasLoopInfo(bb))
        {
            const std::vector<const BasicBlock*>& blocks = getLoopInfo(bb);
            assert(!blocks.empty() && "no available loop info?");
            return blocks.front() == bb;
        }
        return false;
    }

    bool dominate(const BasicBlock* bbKey, const BasicBlock* bbValue) const
    {
        if (bbKey == bbValue)
            return true;

        // An unreachable node is dominated by anything.
        if (isUnreachable(bbValue))
        {
            return true;
        }

        // And dominates nothing.
        if (isUnreachable(bbKey))
        {
            return false;
        }

        const Map<const BasicBlock*,Set<const BasicBlock*>>& dtBBsMap = getDomTreeMap();
        Map<const BasicBlock*,Set<const BasicBlock*>>::const_iterator mapIter = dtBBsMap.find(bbKey);
        if (mapIter != dtBBsMap.end())
        {
            const Set<const BasicBlock*> & dtBBs = mapIter->second;
            if (dtBBs.find(bbValue) != dtBBs.end())
            {
                return true;
            }
        }

        return false;
    }

    bool postDominate(const BasicBlock* bbKey, const BasicBlock* bbValue) const
    {
        if (bbKey == bbValue)
            return true;

        // An unreachable node is dominated by anything.
        if (isUnreachable(bbValue))
        {
            return true;
        }

        // And dominates nothing.
        if (isUnreachable(bbKey))
        {
            return false;
        }

        const Map<const BasicBlock*,Set<const BasicBlock*>>& dtBBsMap = getPostDomTreeMap();
        Map<const BasicBlock*,Set<const BasicBlock*>>::const_iterator mapIter = dtBBsMap.find(bbKey);
        if (mapIter != dtBBsMap.end())
        {
            const Set<const BasicBlock*> & dtBBs = mapIter->second;
            if (dtBBs.find(bbValue) != dtBBs.end())
            {
                return true;
            }
        }
        return false;
    }

    // Dump Control Flow Graph of llvm function, with instructions
    void viewCFG();

    // Dump Control Flow Graph of llvm function, without instructions
    void viewCFGOnly();

};

class SVFGlobal : public SVFValue
{

public:
    SVFGlobal(const std::string& val): SVFValue(val,SVFValue::SVFGlob)
    {
    }

};

class SVFBasicBlock : public SVFValue
{

public:
    SVFBasicBlock(const std::string& val): SVFValue(val,SVFValue::SVFBB)
    {
    }

};

class CallSite
{
private:
    CallBase *CB;
public:
    CallSite(Instruction *I) : CB(SVFUtil::dyn_cast<CallBase>(I)) {}
    CallSite(Value *I) : CB(SVFUtil::dyn_cast<CallBase>(I)) {}

    CallBase *getInstruction() const
    {
        return CB;
    }
    Value *getArgument(unsigned ArgNo) const
    {
        return CB->getArgOperand(ArgNo);
    }
    Type *getType() const
    {
        return CB->getType();
    }
    unsigned arg_size() const
    {
        return CB->arg_size();
    }
    bool arg_empty() const
    {
        return CB->arg_empty();
    }
    Value *getArgOperand(unsigned i) const
    {
        return CB->getArgOperand(i);
    }
    unsigned getNumArgOperands() const
    {
        return CB->arg_size();
    }
    Function *getCalledFunction() const
    {
        return CB->getCalledFunction();
    }
    Value *getCalledValue() const
    {
        return CB->getCalledOperand();
    }
    Function *getCaller() const
    {
        return CB->getCaller();
    }
    FunctionType *getFunctionType() const
    {
        return CB->getFunctionType();
    }
    bool paramHasAttr(unsigned ArgNo, llvm::Attribute::AttrKind Kind) const
    {
        return CB->paramHasAttr(ArgNo, Kind);
    }

    bool operator==(const CallSite &CS) const
    {
        return CB == CS.CB;
    }
    bool operator!=(const CallSite &CS) const
    {
        return CB != CS.CB;
    }
    bool operator<(const CallSite &CS) const
    {
        return getInstruction() < CS.getInstruction();
    }

};

template <typename F, typename S>
OutStream& operator<< (OutStream &o, const std::pair<F, S> &var)
{
    o << "<" << var.first << ", " << var.second << ">";
    return o;
}

} // End namespace SVF

/// Specialise hash for CallSites.
template <> struct std::hash<SVF::CallSite>
{
    size_t operator()(const SVF::CallSite &cs) const
    {
        std::hash<SVF::Instruction *> h;
        return h(cs.getInstruction());
    }
};

#endif /* BASICTYPES_H_ */
