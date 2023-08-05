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
 * File:   interface.h
 * Author:
 *
 * Created on December 14, 2019, 10:03 PM
 */

#ifndef UHDM_INTERFACE_H
#define UHDM_INTERFACE_H

#include <uhdm/sv_vpi_user.h>
#include <uhdm/uhdm_vpi_user.h>

#include <uhdm/SymbolFactory.h>
#include <uhdm/containers.h>
#include <uhdm/instance.h>

#include <uhdm/expr_dist.h>



namespace UHDM {
class clocking_block;
class clocking_block;
class instance_array;


class interface final : public instance {
  UHDM_IMPLEMENT_RTTI(interface, instance)
public:
  // Implicit constructor used to initialize all members,
  // comment: interface();
  virtual ~interface() final = default;


  virtual const BaseClass* VpiParent() const final { return vpiParent_; }

  virtual bool VpiParent(BaseClass* data) final { vpiParent_ = data; if (data) uhdmParentType_ = data->UhdmType(); return true;}

  virtual unsigned int UhdmParentType() const final { return uhdmParentType_; }

  virtual bool UhdmParentType(unsigned int data) final { uhdmParentType_ = data; return true;}

  virtual bool VpiFile(const std::string& data) final;

  virtual const std::string& VpiFile() const final;

  virtual unsigned int UhdmId() const final { return uhdmId_; }

  virtual bool UhdmId(unsigned int data) final { uhdmId_ = data; return true;}

  virtual interface* DeepClone(Serializer* serializer, ElaboratorListener* elab_listener, BaseClass* parent) const override;

  int VpiIndex() const { return vpiIndex_; }

  bool VpiIndex(int data) { vpiIndex_ = data; return true;}

    unsigned int VpiType() const final { return vpiInterface; }

  VectorOfinterface_tf_decl* Interface_tf_decls() const { return interface_tf_decls_; }

  bool Interface_tf_decls(VectorOfinterface_tf_decl* data) { interface_tf_decls_ = data; return true;}

  VectorOfmodport* Modports() const { return modports_; }

  bool Modports(VectorOfmodport* data) { modports_ = data; return true;}

  const clocking_block* Global_clocking() const { return global_clocking_; }

  bool Global_clocking(clocking_block* data) { global_clocking_ = data; return true;}

  const clocking_block* Default_clocking() const { return default_clocking_; }

  bool Default_clocking(clocking_block* data) { default_clocking_ = data; return true;}

  const any* Expr_dist() const { return expr_dist_; }

  bool Expr_dist(any* data) {if (!expr_distGroupCompliant(data)) return false; expr_dist_ = data; return true;}

  const instance_array* Instance_array() const { return instance_array_; }

  bool Instance_array(instance_array* data) { instance_array_ = data; return true;}

  VectorOfmod_path* Mod_paths() const { return mod_paths_; }

  bool Mod_paths(VectorOfmod_path* data) { mod_paths_ = data; return true;}

  VectorOfcont_assign* Cont_assigns() const { return cont_assigns_; }

  bool Cont_assigns(VectorOfcont_assign* data) { cont_assigns_ = data; return true;}

  VectorOfclocking_block* Clocking_blocks() const { return clocking_blocks_; }

  bool Clocking_blocks(VectorOfclocking_block* data) { clocking_blocks_ = data; return true;}

  VectorOfinterface* Interfaces() const { return interfaces_; }

  bool Interfaces(VectorOfinterface* data) { interfaces_ = data; return true;}

  VectorOfinterface_array* Interface_arrays() const { return interface_arrays_; }

  bool Interface_arrays(VectorOfinterface_array* data) { interface_arrays_ = data; return true;}

  VectorOfprocess_stmt* Process() const { return process_; }

  bool Process(VectorOfprocess_stmt* data) { process_ = data; return true;}

  VectorOfport* Ports() const { return ports_; }

  bool Ports(VectorOfport* data) { ports_ = data; return true;}

  VectorOfgen_scope_array* Gen_scope_arrays() const { return gen_scope_arrays_; }

  bool Gen_scope_arrays(VectorOfgen_scope_array* data) { gen_scope_arrays_ = data; return true;}


  virtual  UHDM_OBJECT_TYPE UhdmType() const final { return uhdminterface; }

protected:
  void DeepCopy(interface* clone, Serializer* serializer,
                ElaboratorListener* elaborator, BaseClass* parent) const;

private:

  BaseClass* vpiParent_ = nullptr;

  unsigned int uhdmParentType_ = 0;

  SymbolFactory::ID vpiFile_ = 0;

  unsigned int uhdmId_ = 0;

  int vpiIndex_ = 0;

  VectorOfinterface_tf_decl* interface_tf_decls_ = nullptr;

  VectorOfmodport* modports_ = nullptr;

  clocking_block* global_clocking_ = nullptr;

  clocking_block* default_clocking_ = nullptr;

  any* expr_dist_ = nullptr;

  instance_array* instance_array_ = nullptr;

  VectorOfmod_path* mod_paths_ = nullptr;

  VectorOfcont_assign* cont_assigns_ = nullptr;

  VectorOfclocking_block* clocking_blocks_ = nullptr;

  VectorOfinterface* interfaces_ = nullptr;

  VectorOfinterface_array* interface_arrays_ = nullptr;

  VectorOfprocess_stmt* process_ = nullptr;

  VectorOfport* ports_ = nullptr;

  VectorOfgen_scope_array* gen_scope_arrays_ = nullptr;

};


typedef FactoryT<interface> interfaceFactory;


typedef FactoryT<std::vector<interface *>> VectorOfinterfaceFactory;

}  // namespace UHDM

#endif
