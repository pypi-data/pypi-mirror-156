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
 * File:   case_property_item.h
 * Author:
 *
 * Created on December 14, 2019, 10:03 PM
 */

#ifndef UHDM_CASE_PROPERTY_ITEM_H
#define UHDM_CASE_PROPERTY_ITEM_H

#include <uhdm/sv_vpi_user.h>
#include <uhdm/uhdm_vpi_user.h>

#include <uhdm/SymbolFactory.h>
#include <uhdm/containers.h>
#include <uhdm/BaseClass.h>

#include <uhdm/property_expr_group.h>



namespace UHDM {


class case_property_item final : public BaseClass {
  UHDM_IMPLEMENT_RTTI(case_property_item, BaseClass)
public:
  // Implicit constructor used to initialize all members,
  // comment: case_property_item();
  virtual ~case_property_item() final = default;


  virtual const BaseClass* VpiParent() const final { return vpiParent_; }

  virtual bool VpiParent(BaseClass* data) final { vpiParent_ = data; if (data) uhdmParentType_ = data->UhdmType(); return true;}

  virtual unsigned int UhdmParentType() const final { return uhdmParentType_; }

  virtual bool UhdmParentType(unsigned int data) final { uhdmParentType_ = data; return true;}

  virtual bool VpiFile(const std::string& data) final;

  virtual const std::string& VpiFile() const final;

  virtual unsigned int UhdmId() const final { return uhdmId_; }

  virtual bool UhdmId(unsigned int data) final { uhdmId_ = data; return true;}

  virtual case_property_item* DeepClone(Serializer* serializer, ElaboratorListener* elab_listener, BaseClass* parent) const override;

  VectorOfexpr* Expressions() const { return expressions_; }

  bool Expressions(VectorOfexpr* data) { expressions_ = data; return true;}

  const any* Property_expr() const { return property_expr_; }

  bool Property_expr(any* data) {if (!property_expr_groupGroupCompliant(data)) return false; property_expr_ = data; return true;}

  virtual unsigned int VpiType() const final { return vpiCasePropertyItem; }


  virtual  UHDM_OBJECT_TYPE UhdmType() const final { return uhdmcase_property_item; }

protected:
  void DeepCopy(case_property_item* clone, Serializer* serializer,
                ElaboratorListener* elaborator, BaseClass* parent) const;

private:

  BaseClass* vpiParent_ = nullptr;

  unsigned int uhdmParentType_ = 0;

  SymbolFactory::ID vpiFile_ = 0;

  unsigned int uhdmId_ = 0;

  VectorOfexpr* expressions_ = nullptr;

  any* property_expr_ = nullptr;

};


typedef FactoryT<case_property_item> case_property_itemFactory;


typedef FactoryT<std::vector<case_property_item *>> VectorOfcase_property_itemFactory;

}  // namespace UHDM

#endif
