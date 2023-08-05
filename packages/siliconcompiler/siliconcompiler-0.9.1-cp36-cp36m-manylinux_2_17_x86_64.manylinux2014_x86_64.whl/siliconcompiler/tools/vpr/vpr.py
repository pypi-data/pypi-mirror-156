import os
import siliconcompiler

######################################################################
# Make Docs
######################################################################

def make_docs():
    '''
    VPR (Versatile Place and Route) is an open source CAD
    tool designed for the exploration of new FPGA architectures and
    CAD algorithms, at the packing, placement and routing phases of
    the CAD flow. VPR takes, as input, a description of an FPGA
    architecture along with a technology-mapped user circuit. It
    then performs packing, placement, and routing to map the
    circuit onto the FPGA. The output of VPR includes the FPGA
    configuration needed to implement the circuit and statistics about
    the final mapped design (eg. critical path delay, area, etc).

    Documentation: https://docs.verilogtorouting.org/en/latest

    Sources: https://github.com/verilog-to-routing/vtr-verilog-to-routing

    Installation: https://github.com/verilog-to-routing/vtr-verilog-to-routing

    .. warning::
       Work in progress (not ready for use)
    '''

    chip = siliconcompiler.Chip('<design>')
    chip.set('arg','step', 'apr')
    chip.set('arg','index', '<index>')
    setup(chip)
    return chip

################################
# Setup Tool (pre executable)
################################
def setup(chip):

     tool = 'vpr'
     refdir = 'tools/'+tool
     step = chip.get('arg','step')
     index = chip.get('arg','index')

     chip.set('tool', tool, 'exe', tool, clobber=False)
     chip.set('tool', tool, 'version', '0.0', clobber=False)
     chip.set('tool', tool, 'threads', step, index, os.cpu_count(), clobber=False)

     topmodule = chip.get('design')
     blif = "inputs/" + topmodule + ".blif"

     options = []
     for arch in chip.get('fpga','arch'):
          options.append(arch)

     options.append(blif)

     chip.add('tool', tool, 'option', step, index,  options)

################################
# Post_process (post executable)
################################

def post_process(chip):
    ''' Tool specific function to run after step execution
    '''
    step = chip.get('arg','step')
    index = chip.get('arg','index')

    #TODO: return error code
    return 0

##################################################
if __name__ == "__main__":


    chip = make_docs()
    chip.write_manifest("vpr.json")
