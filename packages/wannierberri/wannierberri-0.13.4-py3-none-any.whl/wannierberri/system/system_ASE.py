#                                                            #
# This file is distributed as part of the WannierBerri code  #
# under the terms of the GNU General Public License. See the #
# file `LICENSE' in the root directory of the WannierBerri   #
# distribution, or http://www.gnu.org/copyleft/gpl.txt       #
#                                                            #
# The WannierBerri code is hosted on GitHub:                 #
# https://github.com/stepan-tsirkin/wannier-berri            #
#                     written by                             #
#           Stepan Tsirkin, University of Zurich             #
#   some parts of this file are originate                    #
# from the translation of Wannier90 code                     #
#------------------------------------------------------------#

import numpy as np
from wannierberri.__utility import real_recip_lattice
from .system_w90 import System_w90
from termcolor import cprint


class System_ASE(System_w90):
    """
    System initialized from the Wannier functions generated by `ASE <https://wiki.fysik.dtu.dk/ase/_modules/ase/dft/wannier.html>`__ .

    Parameters
    ----------
    ase_wannier :
        An object of  `ASE Wannier <https://wiki.fysik.dtu.dk/ase/_modules/ase/dft/wannier.html#Wannier>`__ .

    Notes
    -----
    see also  parameters of the :class:`~wannierberri.System`
    """
    def __init__(
                self,
                ase_wannier,
                ase_R_vectors=False,  # for testing vs ASE
                **parameters):
        self.set_parameters(**parameters)
        self.seedname = "ASE"
        ase_wannier.translate_all_to_cell()
        self.real_lattice, self.recip_lattice = real_recip_lattice(real_lattice=np.array(ase_wannier.unitcell_cc))
        self.mp_grid = ase_wannier.kptgrid

        if not ase_R_vectors:
            self.iRvec, self.Ndegen = self.wigner_seitz(self.mp_grid)
        else:  # enable to do ase-like R-vectors
            N1, N2, N3 = (self.mp_grid - 1) // 2
            self.iRvec = np.array(
                [[n1, n2, n3] for n1 in range(-N1, N1 + 1) for n2 in range(-N2, N2 + 1) for n3 in range(-N3, N3 + 1)],
                dtype=int)
            self.Ndegen = np.ones(self.iRvec.shape[0], dtype=int)

        for i, R in enumerate(self.iRvec):
            if np.all(R == [0, 0, 0]):
                self.iRvec0 = i
                break

        self.nRvec0 = len(self.iRvec)
        self.num_wann = ase_wannier.nwannier
        self.num_kpts = ase_wannier.Nk
        self.wannier_centers_cart_auto = ase_wannier.get_centers()
        print(f"got the Wanier centers : {self.wannier_centers_cart_auto}")
        self.kpt_red = ase_wannier.kpt_kc

        kpt_mp_grid = [
            tuple(k)
            for k in np.array(np.round(self.kpt_red * np.array(self.mp_grid)[None, :]), dtype=int) % self.mp_grid
        ]
        if (0, 0, 0) not in kpt_mp_grid:
            raise ValueError(
                "the grid of k-points read from .chk file is not Gamma-centerred. Please, use Gamma-centered grids in the ab initio calculation"
            )

        self.Ham_R = np.array([ase_wannier.get_hopping(R) / nd for R, nd in zip(self.iRvec, self.Ndegen)]).transpose(
            (1, 2, 0))

        self.getXX_only_wannier_centers()

        self.do_at_end_of_init()

        cprint("Reading the ASE system finished successfully", 'green', attrs=['bold'])

