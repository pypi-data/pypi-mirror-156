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
 * File:   parameter.h
 * Author:
 *
 * Created on December 14, 2019, 10:03 PM
 */

#ifndef UHDM_PARAMETER_H
#define UHDM_PARAMETER_H

#include <uhdm/sv_vpi_user.h>
#include <uhdm/uhdm_vpi_user.h>

#include <uhdm/SymbolFactory.h>
#include <uhdm/containers.h>
#include <uhdm/simple_expr.h>




namespace UHDM {
class expr;
class expr;
class expr;


class parameter final : public simple_expr {
  UHDM_IMPLEMENT_RTTI(parameter, simple_expr)
public:
  // Implicit constructor used to initialize all members,
  // comment: parameter();
  virtual ~parameter() final = default;


  virtual const BaseClass* VpiParent() const final { return vpiParent_; }

  virtual bool VpiParent(BaseClass* data) final { vpiParent_ = data; if (data) uhdmParentType_ = data->UhdmType(); return true;}

  virtual unsigned int UhdmParentType() const final { return uhdmParentType_; }

  virtual bool UhdmParentType(unsigned int data) final { uhdmParentType_ = data; return true;}

  virtual bool VpiFile(const std::string& data) final;

  virtual const std::string& VpiFile() const final;

  virtual unsigned int UhdmId() const final { return uhdmId_; }

  virtual bool UhdmId(unsigned int data) final { uhdmId_ = data; return true;}

  virtual parameter* DeepClone(Serializer* serializer, ElaboratorListener* elab_listener, BaseClass* parent) const override;

  int VpiConstType() const { return vpiConstType_; }

  bool VpiConstType(int data) { vpiConstType_ = data; return true;}

  bool VpiSigned() const { return vpiSigned_; }

  bool VpiSigned(bool data) { vpiSigned_ = data; return true;}

  const expr* Expr() const { return expr_; }

  bool Expr(expr* data) { expr_ = data; return true;}

  VectorOfrange* Ranges() const { return ranges_; }

  bool Ranges(VectorOfrange* data) { ranges_ = data; return true;}

  const expr* Left_range() const { return left_range_; }

  bool Left_range(expr* data) { left_range_ = data; return true;}

  const expr* Right_range() const { return right_range_; }

  bool Right_range(expr* data) { right_range_ = data; return true;}

  bool VpiLocalParam() const { return vpiLocalParam_; }

  bool VpiLocalParam(bool data) { vpiLocalParam_ = data; return true;}

  virtual bool VpiName(const std::string& data) final;

  virtual const std::string& VpiName() const final;

  bool VpiFullName(const std::string& data);

  const std::string&  VpiFullName() const;

  bool VpiImported(const std::string& data);

  const std::string& VpiImported() const;

  virtual unsigned int VpiType() const final { return vpiParameter; }


  virtual  UHDM_OBJECT_TYPE UhdmType() const final { return uhdmparameter; }

protected:
  void DeepCopy(parameter* clone, Serializer* serializer,
                ElaboratorListener* elaborator, BaseClass* parent) const;

private:

  BaseClass* vpiParent_ = nullptr;

  unsigned int uhdmParentType_ = 0;

  SymbolFactory::ID vpiFile_ = 0;

  unsigned int uhdmId_ = 0;

  int vpiConstType_ = 0;

  bool vpiSigned_ = 0;

  expr* expr_ = nullptr;

  VectorOfrange* ranges_ = nullptr;

  expr* left_range_ = nullptr;

  expr* right_range_ = nullptr;

  bool vpiLocalParam_ = 0;

  SymbolFactory::ID vpiName_ = 0;

  SymbolFactory::ID vpiFullName_ = 0;

  SymbolFactory::ID vpiImported_ = 0;

};


typedef FactoryT<parameter> parameterFactory;


typedef FactoryT<std::vector<parameter *>> VectorOfparameterFactory;

}  // namespace UHDM

#endif
