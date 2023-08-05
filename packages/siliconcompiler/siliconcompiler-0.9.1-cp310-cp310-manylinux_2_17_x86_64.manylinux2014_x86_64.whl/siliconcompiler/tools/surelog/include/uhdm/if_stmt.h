/*
 Do not modify, auto-generated by model_gen.tcl

 Copyright 2019 Alain Dargelas

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 */

/*
 * File:   if_stmt.h
 * Author:
 *
 * Created on December 14, 2019, 10:03 PM
 */

#ifndef UHDM_IF_STMT_H
#define UHDM_IF_STMT_H

#include <uhdm/sv_vpi_user.h>
#include <uhdm/uhdm_vpi_user.h>

#include <uhdm/SymbolFactory.h>
#include <uhdm/containers.h>
#include <uhdm/atomic_stmt.h>

#include <uhdm/stmt.h>



namespace UHDM {
class expr;


class if_stmt final : public atomic_stmt {
  UHDM_IMPLEMENT_RTTI(if_stmt, atomic_stmt)
public:
  // Implicit constructor used to initialize all members,
  // comment: if_stmt();
  virtual ~if_stmt() final = default;


  virtual const BaseClass* VpiParent() const final { return vpiParent_; }

  virtual bool VpiParent(BaseClass* data) final { vpiParent_ = data; if (data) uhdmParentType_ = data->UhdmType(); return true;}

  virtual unsigned int UhdmParentType() const final { return uhdmParentType_; }

  virtual bool UhdmParentType(unsigned int data) final { uhdmParentType_ = data; return true;}

  virtual bool VpiFile(const std::string& data) final;

  virtual const std::string& VpiFile() const final;

  virtual unsigned int UhdmId() const final { return uhdmId_; }

  virtual bool UhdmId(unsigned int data) final { uhdmId_ = data; return true;}

  virtual if_stmt* DeepClone(Serializer* serializer, ElaboratorListener* elab_listener, BaseClass* parent) const override;

    unsigned int VpiType() const final { return vpiIf; }

  int VpiQualifier() const { return vpiQualifier_; }

  bool VpiQualifier(int data) { vpiQualifier_ = data; return true;}

  const expr* VpiCondition() const { return vpiCondition_; }

  bool VpiCondition(expr* data) { vpiCondition_ = data; return true;}

  const any* VpiStmt() const { return vpiStmt_; }

  bool VpiStmt(any* data) {if (!stmtGroupCompliant(data)) return false; vpiStmt_ = data; return true;}


  virtual  UHDM_OBJECT_TYPE UhdmType() const final { return uhdmif_stmt; }

protected:
  void DeepCopy(if_stmt* clone, Serializer* serializer,
                ElaboratorListener* elaborator, BaseClass* parent) const;

private:

  BaseClass* vpiParent_ = nullptr;

  unsigned int uhdmParentType_ = 0;

  SymbolFactory::ID vpiFile_ = 0;

  unsigned int uhdmId_ = 0;

  int vpiQualifier_ = 0;

  expr* vpiCondition_ = nullptr;

  any* vpiStmt_ = nullptr;

};


typedef FactoryT<if_stmt> if_stmtFactory;


typedef FactoryT<std::vector<if_stmt *>> VectorOfif_stmtFactory;

}  // namespace UHDM

#endif
