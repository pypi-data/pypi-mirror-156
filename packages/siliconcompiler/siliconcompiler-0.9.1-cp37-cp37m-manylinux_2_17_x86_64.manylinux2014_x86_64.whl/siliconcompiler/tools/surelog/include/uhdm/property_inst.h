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
 * File:   property_inst.h
 * Author:
 *
 * Created on December 14, 2019, 10:03 PM
 */

#ifndef UHDM_PROPERTY_INST_H
#define UHDM_PROPERTY_INST_H

#include <uhdm/sv_vpi_user.h>
#include <uhdm/uhdm_vpi_user.h>

#include <uhdm/SymbolFactory.h>
#include <uhdm/containers.h>
#include <uhdm/BaseClass.h>

#include <uhdm/expr_dist.h>
#include <uhdm/property_expr_named_event_group.h>



namespace UHDM {
class property_decl;
class clocking_block;


class property_inst final : public BaseClass {
  UHDM_IMPLEMENT_RTTI(property_inst, BaseClass)
public:
  // Implicit constructor used to initialize all members,
  // comment: property_inst();
  virtual ~property_inst() final = default;


  virtual const BaseClass* VpiParent() const final { return vpiParent_; }

  virtual bool VpiParent(BaseClass* data) final { vpiParent_ = data; if (data) uhdmParentType_ = data->UhdmType(); return true;}

  virtual unsigned int UhdmParentType() const final { return uhdmParentType_; }

  virtual bool UhdmParentType(unsigned int data) final { uhdmParentType_ = data; return true;}

  virtual bool VpiFile(const std::string& data) final;

  virtual const std::string& VpiFile() const final;

  virtual unsigned int UhdmId() const final { return uhdmId_; }

  virtual bool UhdmId(unsigned int data) final { uhdmId_ = data; return true;}

  virtual property_inst* DeepClone(Serializer* serializer, ElaboratorListener* elab_listener, BaseClass* parent) const override;

  const any* VpiDisableCondition() const { return vpiDisableCondition_; }

  bool VpiDisableCondition(any* data) {if (!expr_distGroupCompliant(data)) return false; vpiDisableCondition_ = data; return true;}

  VectorOfany* VpiArguments() const { return vpiArguments_; }

  bool VpiArguments(VectorOfany* data) {if (!property_expr_named_event_groupGroupCompliant(data)) return false; vpiArguments_ = data; return true;}

  const property_decl* Property_decl() const { return property_decl_; }

  bool Property_decl(property_decl* data) { property_decl_ = data; return true;}

  int VpiStartLine() const { return vpiStartLine_; }

  bool VpiStartLine(int data) { vpiStartLine_ = data; return true;}

  int VpiColumn() const { return vpiColumn_; }

  bool VpiColumn(int data) { vpiColumn_ = data; return true;}

  int VpiEndLine() const { return vpiEndLine_; }

  bool VpiEndLine(int data) { vpiEndLine_ = data; return true;}

  int VpiEndColumn() const { return vpiEndColumn_; }

  bool VpiEndColumn(int data) { vpiEndColumn_ = data; return true;}

  virtual bool VpiName(const std::string& data) final;

  virtual const std::string& VpiName() const final;

  const clocking_block* Clocking_block() const { return clocking_block_; }

  bool Clocking_block(clocking_block* data) { clocking_block_ = data; return true;}

  virtual unsigned int VpiType() const final { return vpiPropertyInst; }


  virtual  UHDM_OBJECT_TYPE UhdmType() const final { return uhdmproperty_inst; }

protected:
  void DeepCopy(property_inst* clone, Serializer* serializer,
                ElaboratorListener* elaborator, BaseClass* parent) const;

private:

  BaseClass* vpiParent_ = nullptr;

  unsigned int uhdmParentType_ = 0;

  SymbolFactory::ID vpiFile_ = 0;

  unsigned int uhdmId_ = 0;

  any* vpiDisableCondition_ = nullptr;

  VectorOfany* vpiArguments_ = nullptr;

  property_decl* property_decl_ = nullptr;

  int vpiStartLine_ = 0;

  int vpiColumn_ = 0;

  int vpiEndLine_ = 0;

  int vpiEndColumn_ = 0;

  SymbolFactory::ID vpiName_ = 0;

  clocking_block* clocking_block_ = nullptr;

};


typedef FactoryT<property_inst> property_instFactory;


typedef FactoryT<std::vector<property_inst *>> VectorOfproperty_instFactory;

}  // namespace UHDM

#endif
