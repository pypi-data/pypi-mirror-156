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
 * File:   net_drivers.h
 * Author:
 *
 * Created on December 14, 2019, 10:03 PM
 */

#ifndef UHDM_NET_DRIVERS_H
#define UHDM_NET_DRIVERS_H

#include <uhdm/sv_vpi_user.h>
#include <uhdm/uhdm_vpi_user.h>

#include <uhdm/SymbolFactory.h>
#include <uhdm/containers.h>
#include <uhdm/BaseClass.h>




namespace UHDM {


class net_drivers : public BaseClass {
  UHDM_IMPLEMENT_RTTI(net_drivers, BaseClass)
public:
  // Implicit constructor used to initialize all members,
  // comment: net_drivers();
  virtual ~net_drivers() = default;


  virtual net_drivers* DeepClone(Serializer* serializer, ElaboratorListener* elab_listener, BaseClass* parent) const override = 0;


  virtual  UHDM_OBJECT_TYPE UhdmType() const override { return uhdmnet_drivers; }

protected:
  void DeepCopy(net_drivers* clone, Serializer* serializer,
                ElaboratorListener* elaborator, BaseClass* parent) const;

private:

};

#if 0 // This class cannot be instantiated
typedef FactoryT<net_drivers> net_driversFactory;
#endif

typedef FactoryT<std::vector<net_drivers *>> VectorOfnet_driversFactory;

}  // namespace UHDM

#endif
