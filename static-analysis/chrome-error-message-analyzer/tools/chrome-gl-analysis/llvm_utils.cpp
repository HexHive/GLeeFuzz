#include "llvm_utils.hpp"

#include "Util/SVFUtil.h"

#include <llvm/IR/Constants.h>
#include <llvm/IR/GlobalVariable.h>
// #include <llvm/IR/Instruction.h>
#include <llvm/IR/Instructions.h>
#include <llvm/Support/raw_ostream.h>

#include <assert.h>

#if LLVM_VERSION_MAJOR < 11
#include <llvm/IR/CallSite.h>
#else
#include <llvm/IR/AbstractCallSite.h>
#endif

#define ERR_MSG_ARG_IDX 3
#define ERR_CODE_ARG_IDX 1
tuple<string, int>
extract_log_message_from_callinst(const llvm::Instruction *callinst) {
    // callinst is a call to the log function

    if (const auto *ci = llvm::dyn_cast<llvm::CallInst>(callinst)) {
#if LLVM_VERSION_MAJOR < 11
        llvm::ImmutableCallSite cs(ci);
#else
        llvm::AbstractCallSite cs(&ci->getCalledOperandUse());
#endif

        if (cs.getCalledFunction()->getName().str() != getLogFunctionName()) {
            llvm::outs() << "Not calling to the log function\n";
            return make_tuple("", -1);
        }

        // the log message is the third argument
        // FIXME: some argument are not constant
        // and thus can not be parse simply using this way
        if (cs.getNumArgOperands() < ERR_MSG_ARG_IDX + 1) {
            llvm::outs() << "Not enough arguments are passed in\n";
            assert(false);
            return make_tuple("Not-Enough-ARGS-TO-ERR-EMIT-FUNC", -1);
        }

        bool resolved = false;
#if LLVM_VERSION_MAJOR < 11
        string res = get_const_string_val(cs.getArgOperand(ERR_MSG_ARG_IDX), resolved);
#else
        string res = get_const_string_val(cs.getCallArgOperand(ERR_MSG_ARG_IDX), resolved);
#endif
        if (!resolved) {
            string srcLoc = SVF::SVFUtil::getSourceLoc(callinst);
            llvm::outs() << "unresolved error message at " << srcLoc <<"\n";
            return make_tuple(srcLoc, -1);
        }

#if LLVM_VERSION_MAJOR < 11
        return make_tuple(res, get_const_int_val(cs.getArgOperand(ERR_CODE_ARG_IDX));
#else
        return make_tuple(res, get_const_int_val(cs.getCallArgOperand(ERR_CODE_ARG_IDX)));
#endif
    }

    llvm::outs() << "Not a CallInst\n";
    assert(false);
    return make_tuple("", -1);
}

string get_const_string_from_global(const llvm::GlobalVariable *gv) {

    if (gv->hasInitializer()) {
        const llvm::Constant *c = gv->getInitializer();

        if (const auto *ca =
            llvm::dyn_cast<llvm::ConstantDataArray>(c)) {

#if LLVM_VERSION_MAJOR < 11
            return ca->getAsCString();
#else
            return ca->getAsCString().str();
#endif
        } else {
            llvm::outs() << "Not ConstantDataArray\n";
        }
    } else {
        llvm::outs() << "Not Having Initializer\n";
    }

    return "";
}


string get_const_string_val(const llvm::Value *val, bool &resolved) {

    if (const auto *ge = llvm::dyn_cast<llvm::ConstantExpr>(val)) {
        //Sometimes this is considered as ConstantExpr
        // i8* getelementptr inbounds ([26 x i8], [26 x i8]* @.str.31.1142,
        // i64 0, i64 0)
        llvm::Value *v = ge->getOperand(0);
        if (const auto *gv = llvm::dyn_cast<llvm::GlobalVariable>(v)) {
            resolved = true;
            return get_const_string_from_global(gv);
        }
    } else if (const auto *gep = llvm::dyn_cast<llvm::GetElementPtrInst>(val)) {
        // hanlde GEP
        // as shown below
        //  call void @_ZN5blink25WebGLRenderingContextBase17SynthesizeGLErrorEjPKcS2_NS0_24ConsoleDisplayPreferenceE(%"class.blink::WebGLRenderingContextBase"* %5,
        //  i32 1280,
        //  i8* getelementptr inbounds ([14 x i8], [14 x i8]* @.str.30.1141, i64 0, i64 0),
        //  i8* getelementptr inbounds ([26 x i8], [26 x i8]* @.str.31.1142, i64 0, i64 0),
        //  i32 0), !dbg !261242
        const llvm::Value *ptr_val = gep->getPointerOperand();
        if (const auto *gv = llvm::dyn_cast<llvm::GlobalVariable>(ptr_val)) {
            resolved = true;
            return  get_const_string_from_global(gv);
        } else {
            llvm::outs() << "ptr not a global variable\n";
        }
    } else {
        llvm::outs() << "Neither a GlobalVariable nor a LoadInst\n";
    }

    resolved = false;
    return "";
}

int get_const_int_val(const llvm::Value *val) {
    if (const auto *ci = llvm::dyn_cast<llvm::ConstantInt>(val)) {
        if (ci->getBitWidth() <= 32) {
            return (int)ci->getSExtValue();
        }
    }

    return -1;
}


string &getLogFunctionName() {
  static string __log_function_name =
    "_ZN5blink25WebGLRenderingContextBase17Synthesize"
    "GLErrorEjPKcS2_NS0_24ConsoleDisplayPreferenceE";

  return __log_function_name;
}
