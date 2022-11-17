#ifndef INST_VISITOR_H_
#define INST_VISITOR_H_

#include "Util/BasicTypes.h"

class MyInstVisitor : public llvm::InstVisitor<MyInstVisitor> {

  private:
    std::set<const llvm::Value *> &values;

  public:
    MyInstVisitor(std::set<const llvm::Value *> &values) : values(values) {}

    void addValue(const llvm::Value *v) { values.insert(v); }

    std::set<const llvm::Value *> &getResults() { return values; }
};

#endif // INST_VISITOR_H_
