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
 * File:   reg_array.h
 * Author:
 *
 * Created on December 14, 2019, 10:03 PM
 */

#ifndef UHDM_REG_ARRAY_H
#define UHDM_REG_ARRAY_H

#include <uhdm/sv_vpi_user.h>
#include <uhdm/uhdm_vpi_user.h>

#include <uhdm/SymbolFactory.h>
#include <uhdm/containers.h>
#include <uhdm/BaseClass.h>




namespace UHDM {
class expr;
class expr;


class reg_array final : public BaseClass {
  UHDM_IMPLEMENT_RTTI(reg_array, BaseClass)
public:
  // Implicit constructor used to initialize all members,
  // comment: reg_array();
  virtual ~reg_array() final = default;


  virtual const BaseClass* VpiParent() const final { return vpiParent_; }

  virtual bool VpiParent(BaseClass* data) final { vpiParent_ = data; if (data) uhdmParentType_ = data->UhdmType(); return true;}

  virtual unsigned int UhdmParentType() const final { return uhdmParentType_; }

  virtual bool UhdmParentType(unsigned int data) final { uhdmParentType_ = data; return true;}

  virtual bool VpiFile(const std::string& data) final;

  virtual const std::string& VpiFile() const final;

  virtual unsigned int UhdmId() const final { return uhdmId_; }

  virtual bool UhdmId(unsigned int data) final { uhdmId_ = data; return true;}

  virtual reg_array* DeepClone(Serializer* serializer, ElaboratorListener* elab_listener, BaseClass* parent) const override;

  bool VpiIsMemory() const { return vpiIsMemory_; }

  bool VpiIsMemory(bool data) { vpiIsMemory_ = data; return true;}

  const expr* Left_expr() const { return left_expr_; }

  bool Left_expr(expr* data) { left_expr_ = data; return true;}

  const expr* Right_expr() const { return right_expr_; }

  bool Right_expr(expr* data) { right_expr_ = data; return true;}

  VectorOfreg* Regs() const { return regs_; }

  bool Regs(VectorOfreg* data) { regs_ = data; return true;}

  virtual unsigned int VpiType() const final { return vpiRegArray; }


  virtual  UHDM_OBJECT_TYPE UhdmType() const final { return uhdmreg_array; }

protected:
  void DeepCopy(reg_array* clone, Serializer* serializer,
                ElaboratorListener* elaborator, BaseClass* parent) const;

private:

  BaseClass* vpiParent_ = nullptr;

  unsigned int uhdmParentType_ = 0;

  SymbolFactory::ID vpiFile_ = 0;

  unsigned int uhdmId_ = 0;

  bool vpiIsMemory_ = 0;

  expr* left_expr_ = nullptr;

  expr* right_expr_ = nullptr;

  VectorOfreg* regs_ = nullptr;

};


typedef FactoryT<reg_array> reg_arrayFactory;


typedef FactoryT<std::vector<reg_array *>> VectorOfreg_arrayFactory;

}  // namespace UHDM

#endif
