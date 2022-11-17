#ifndef LLVM_UTILS_H_
#define LLVM_UTILS_H_

#include <set>
#include <tuple>
#include <string>

#include <llvm/IR/Function.h>
#include <llvm/IR/Value.h>
#include <llvm/IR/Instructions.h>

using namespace std;

tuple<string, int>
extract_log_message_from_callinst(const llvm::Instruction *callinst);
string get_const_string_val(const llvm::Value *val, bool &resolved);
string get_const_string_from_global(const llvm::GlobalVariable *gv);
string get_const_stl_string_val(const llvm::Value *val);
int get_const_int_val(const llvm::Value *val);
string &getLogFunctionName();

#endif // LLVM_UTILS_H_
