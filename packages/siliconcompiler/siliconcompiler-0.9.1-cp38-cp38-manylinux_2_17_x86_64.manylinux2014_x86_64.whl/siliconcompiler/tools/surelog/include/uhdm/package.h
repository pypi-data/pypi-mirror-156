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
 * File:   package.h
 * Author:
 *
 * Created on December 14, 2019, 10:03 PM
 */

#ifndef UHDM_PACKAGE_H
#define UHDM_PACKAGE_H

#include <uhdm/sv_vpi_user.h>
#include <uhdm/uhdm_vpi_user.h>

#include <uhdm/SymbolFactory.h>
#include <uhdm/containers.h>
#include <uhdm/instance.h>




namespace UHDM {


class package final : public instance {
  UHDM_IMPLEMENT_RTTI(package, instance)
public:
  // Implicit constructor used to initialize all members,
  // comment: package();
  virtual ~package() final = default;


  virtual const BaseClass* VpiParent() const final { return vpiParent_; }

  virtual bool VpiParent(BaseClass* data) final { vpiParent_ = data; if (data) uhdmParentType_ = data->UhdmType(); return true;}

  virtual unsigned int UhdmParentType() const final { return uhdmParentType_; }

  virtual bool UhdmParentType(unsigned int data) final { uhdmParentType_ = data; return true;}

  virtual bool VpiFile(const std::string& data) final;

  virtual const std::string& VpiFile() const final;

  virtual unsigned int UhdmId() const final { return uhdmId_; }

  virtual bool UhdmId(unsigned int data) final { uhdmId_ = data; return true;}

  virtual package* DeepClone(Serializer* serializer, ElaboratorListener* elab_listener, BaseClass* parent) const override;

    unsigned int VpiType() const final { return vpiPackage; }

  bool VpiUnit() const { return vpiUnit_; }

  bool VpiUnit(bool data) { vpiUnit_ = data; return true;}


  virtual  UHDM_OBJECT_TYPE UhdmType() const final { return uhdmpackage; }

protected:
  void DeepCopy(package* clone, Serializer* serializer,
                ElaboratorListener* elaborator, BaseClass* parent) const;

private:

  BaseClass* vpiParent_ = nullptr;

  unsigned int uhdmParentType_ = 0;

  SymbolFactory::ID vpiFile_ = 0;

  unsigned int uhdmId_ = 0;

  bool vpiUnit_ = 0;

};


typedef FactoryT<package> packageFactory;


typedef FactoryT<std::vector<package *>> VectorOfpackageFactory;

}  // namespace UHDM

#endif
