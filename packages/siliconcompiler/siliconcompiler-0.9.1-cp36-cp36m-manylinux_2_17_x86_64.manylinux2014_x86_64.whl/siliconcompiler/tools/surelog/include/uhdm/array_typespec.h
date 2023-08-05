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
 * File:   array_typespec.h
 * Author:
 *
 * Created on December 14, 2019, 10:03 PM
 */

#ifndef UHDM_ARRAY_TYPESPEC_H
#define UHDM_ARRAY_TYPESPEC_H

#include <uhdm/sv_vpi_user.h>
#include <uhdm/uhdm_vpi_user.h>

#include <uhdm/SymbolFactory.h>
#include <uhdm/containers.h>
#include <uhdm/typespec.h>




namespace UHDM {
class expr;
class expr;
class typespec;
class typespec;


class array_typespec final : public typespec {
  UHDM_IMPLEMENT_RTTI(array_typespec, typespec)
public:
  // Implicit constructor used to initialize all members,
  // comment: array_typespec();
  virtual ~array_typespec() final = default;


  virtual const BaseClass* VpiParent() const final { return vpiParent_; }

  virtual bool VpiParent(BaseClass* data) final { vpiParent_ = data; if (data) uhdmParentType_ = data->UhdmType(); return true;}

  virtual unsigned int UhdmParentType() const final { return uhdmParentType_; }

  virtual bool UhdmParentType(unsigned int data) final { uhdmParentType_ = data; return true;}

  virtual bool VpiFile(const std::string& data) final;

  virtual const std::string& VpiFile() const final;

  virtual unsigned int UhdmId() const final { return uhdmId_; }

  virtual bool UhdmId(unsigned int data) final { uhdmId_ = data; return true;}

  virtual array_typespec* DeepClone(Serializer* serializer, ElaboratorListener* elab_listener, BaseClass* parent) const override;

  int VpiArrayType() const { return vpiArrayType_; }

  bool VpiArrayType(int data) { vpiArrayType_ = data; return true;}

  VectorOfrange* Ranges() const { return ranges_; }

  bool Ranges(VectorOfrange* data) { ranges_ = data; return true;}

  const expr* Left_expr() const { return left_expr_; }

  bool Left_expr(expr* data) { left_expr_ = data; return true;}

  const expr* Right_expr() const { return right_expr_; }

  bool Right_expr(expr* data) { right_expr_ = data; return true;}

  const typespec* Index_typespec() const { return index_typespec_; }

  bool Index_typespec(typespec* data) { index_typespec_ = data; return true;}

  const typespec* Elem_typespec() const { return elem_typespec_; }

  bool Elem_typespec(typespec* data) { elem_typespec_ = data; return true;}

  virtual unsigned int VpiType() const final { return vpiArrayTypespec; }


  virtual  UHDM_OBJECT_TYPE UhdmType() const final { return uhdmarray_typespec; }

protected:
  void DeepCopy(array_typespec* clone, Serializer* serializer,
                ElaboratorListener* elaborator, BaseClass* parent) const;

private:

  BaseClass* vpiParent_ = nullptr;

  unsigned int uhdmParentType_ = 0;

  SymbolFactory::ID vpiFile_ = 0;

  unsigned int uhdmId_ = 0;

  int vpiArrayType_ = 0;

  VectorOfrange* ranges_ = nullptr;

  expr* left_expr_ = nullptr;

  expr* right_expr_ = nullptr;

  typespec* index_typespec_ = nullptr;

  typespec* elem_typespec_ = nullptr;

};


typedef FactoryT<array_typespec> array_typespecFactory;


typedef FactoryT<std::vector<array_typespec *>> VectorOfarray_typespecFactory;

}  // namespace UHDM

#endif
