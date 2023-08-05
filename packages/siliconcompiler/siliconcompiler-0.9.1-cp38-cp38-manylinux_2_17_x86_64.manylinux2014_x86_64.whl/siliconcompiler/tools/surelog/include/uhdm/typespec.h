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
 * File:   typespec.h
 * Author:
 *
 * Created on December 14, 2019, 10:03 PM
 */

#ifndef UHDM_TYPESPEC_H
#define UHDM_TYPESPEC_H

#include <uhdm/sv_vpi_user.h>
#include <uhdm/uhdm_vpi_user.h>

#include <uhdm/SymbolFactory.h>
#include <uhdm/containers.h>
#include <uhdm/BaseClass.h>




namespace UHDM {
class typespec;
class instance;


class typespec : public BaseClass {
  UHDM_IMPLEMENT_RTTI(typespec, BaseClass)
public:
  // Implicit constructor used to initialize all members,
  // comment: typespec();
  virtual ~typespec() = default;


  virtual typespec* DeepClone(Serializer* serializer, ElaboratorListener* elab_listener, BaseClass* parent) const override = 0;

  virtual bool VpiName(const std::string& data) final;

  virtual const std::string& VpiName() const final;

  const typespec* Typedef_alias() const { return typedef_alias_; }

  bool Typedef_alias(typespec* data) { typedef_alias_ = data; return true;}

  const instance* Instance() const { return instance_; }

  bool Instance(instance* data) { instance_ = data; return true;}


  virtual  UHDM_OBJECT_TYPE UhdmType() const override { return uhdmtypespec; }

protected:
  void DeepCopy(typespec* clone, Serializer* serializer,
                ElaboratorListener* elaborator, BaseClass* parent) const;

private:

  SymbolFactory::ID vpiName_ = 0;

  typespec* typedef_alias_ = nullptr;

  instance* instance_ = nullptr;

};

#if 0 // This class cannot be instantiated
typedef FactoryT<typespec> typespecFactory;
#endif

typedef FactoryT<std::vector<typespec *>> VectorOftypespecFactory;

}  // namespace UHDM

#endif
