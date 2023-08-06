"""
This file defines the class PolarGrid, which implements the polarity model coupled to a PDE describing the evolution of ligand density around the growing organoid

Be very careful with grid spacing!!!! Number of variables grows with the cube of the inverse grid spacing.
"""
from .polarcore import PolarWNT
import numpy as np
import torch


class PolarPDE(PolarWNT):
    def __init__(self, *args,
                 bounding_radius_factor=2,
                 contact_radius=1,
                 R_init=1.0,
                 a=0.8,
                 gamma=0.1,
                 b=1.0,
                 D=100,
                 hill_coefficient=8,
                 hill_k=0.55,
                 grid_N=100,
                 grid_dx=0.5,
                 beta_func_of_w_exponent=1,
                 **kwargs):
        self.bounding_radius_factor = bounding_radius_factor
        self.contact_radius = contact_radius
        super().__init__(*args, **kwargs)
        self.R = (2*torch.rand(*self.w.shape, requires_grad=False,
                  device=self.device)) * R_init
        self.R.requires_grad = False
        self.R_init = R_init
        # intrinsic receptor production rate (as a multiple of gamma)
        self.a = a
        # intrinsic ligand production rate (as a multiple of gamma)
        self.b = b
        self.gamma = gamma                  # intrinsic decay rate of receptor
        self.D = D                          # diffusion ratio of ligand vs. receptor
        self.grid_N = grid_N                # number of gridpoints in each dimension
        self.grid_dx = grid_dx              # spatial distance between adjacent gridpoints
        self.beta_func_of_w_exponent = beta_func_of_w_exponent
        # initialize a 3d tensor to hold the ligand level in space
        self.L = torch.zeros(
            (self.grid_N, self.grid_N, self.grid_N), device=self.device)
        self.stencil_3d_conv = torch.tensor([[[2, 3, 2], [3, 6, 3], [2, 3, 2]],
                                             [[3, 6, 3], [6, -88, 6], [3, 6, 3]],
                                             [[2, 3, 2], [3, 6, 3], [2, 3, 2]]], device=self.device) / (26*self.grid_dx**2)
        # create a tensor giving spatial positions corresponding to indices of self.L
        Lcoords = self.grid_dx * \
            (torch.arange(self.grid_N, device=self.device) - (self.grid_N - 1)/2)
        self.L_grid = torch.stack(torch.meshgrid(
            (Lcoords, Lcoords, Lcoords), indexing='ij'), dim=-1)
        self.hill_coefficient = hill_coefficient
        self.hill_k = hill_k
        self.get_bounding_sphere()

    def get_bounding_sphere(self):
        self.bounding_sphere_center = self.x.mean(dim=0).detach()
        self.bounding_sphere_radius = (self.bounding_radius_factor *
                                       torch.max(torch.norm(self.x - self.bounding_sphere_center, dim=1))).detach()
        return self.bounding_sphere_center, self.bounding_sphere_radius

    def hill_function(self, x):
        return x**self.hill_coefficient / (self.hill_k**self.hill_coefficient + x**self.hill_coefficient)

    def laplacian_R(self):
        """
        Computes the laplacian of the R concentration field
        computes the graph laplacian according to "true neighbors" including nearest-neighbor distances 
        normalization is tricky since neighbor-pairs are not in orthogonal directions...
            i think this means we should normalize by 4/(# neighbors)
        """
        self.find_true_neighbours()
        # return ((self.R[self.idx]- self.idx.shape[1]*self.R[:, None]) / self.d**2).sum(dim=1) * (4/self.idx.shape[1])
        return ((self.R[self.idx] - self.idx.shape[1]*self.R[:,None])/self.d.detach()**2).sum(dim=1) * (4/self.idx.shape[1])

    def laplacian_L(self):
        """
        computes the laplacian of the continuous field L, which is defined on a 3D rectangular grid with uniform spacing dx

        math formula: laplacian_x[i,j,k] = ((x[i+1,j,k] + x[i-1,j,k] + x[i,j+1,k] + x[i,j-1,k] + x[i,j,k+1] + x[i,j,k-1]) - 6 * x[i,j,k])/x**2
        This holds for i,j,k in the /interior/ of the cube; if any of i,j,k +/- 1 is not in the domain, replace it with i,j,k

        I want to do this with clever indexing and padding
        """
        A = torch.cat((self.L[1:, :, :], self.L[-1:, :, :]),
                      dim=0)  # A[i,j,k] = self.L[i+1,j,k]
        # B[i,j,k] = self.L[i-1,j,k]
        B = torch.cat((self.L[:1, :, :], self.L[:-1, :, :]), dim=0)
        # C[i,j,k] = self.L[i,j+1,k]
        C = torch.cat((self.L[:, 1:, :], self.L[:, -1:, :]), dim=1)
        # D[i,j,k] = self.L[i,j-1,k]
        D = torch.cat((self.L[:, :1, :], self.L[:, :-1, :]), dim=1)
        # E[i,j,k] = self.L[i,j,k+1]
        E = torch.cat((self.L[:, :, 1:], self.L[:, :, -1:]), dim=2)
        # F[i,j,k] = self.L[i,j,k-1]
        F = torch.cat((self.L[:, :, :1], self.L[:, :, :-1]), dim=2)
        return (A+B+C+D+E+F - 6*self.L)/(self.grid_dx**2)

    def laplacian_L_27_point(self):
        """
        Implements the 27-point laplacian stencil, which should be more numerically stable than the 7-point one above
        """
        # first pad L with identical data in each dimension
        Lpad = torch.nn.functional.pad(self.L[None,None,:,:,:], (1,1,1,1,1,1), 'replicate')
        return torch.nn.functional.conv3d(Lpad, self.stencil_3d_conv[None, None, :, :])[0, 0]

    def closest_gridpoints(self):
        """
        Finds closest gridpoint to cell locations

        NOTE: Relies on the spatial locations are defined in the same way in each dimension, i.e. the spatial grid is cubic and does not change
        In particular index i corresponds to spatial location (i-(N-1)/2)*dx

        INPUT:
            self.x = tensor of shape (N, 3) containing (x,y,z)-coordinates of N points, to which we want the closest gridpoint
            self.grid_dx = spatial distance between grid points along each dimension
            self.grid_N = number of spatial grid points in each dimension

        OUTPUT:
            idx = tuple of tensors, each of length N
                  index into a 3D tensor by doing L[idx]
        """
        # check if any coordinates are outside
        if self.x.max() > self.grid_dx*(self.grid_N - 1)/2 or self.x.min() < -self.grid_dx*(self.grid_N - 1)/2:
            raise RuntimeError('cell positions out of bounds')
        idxs_2d = torch.round(self.x/self.grid_dx +
                              (self.grid_N - 1)/2).long().chunk(chunks=3, dim=1)
        return tuple(ind.squeeze() for ind in idxs_2d)

    def L_source_indices(self):
        """
        This routine finds the 3-dimensional indices of gridpoints where L should be produced.
        At the moment this will be  all gridpoints OUTSIDE of the bouding sphere

        This may end up capturing a lot of compute time, could be a place to look in the future to speed up by figuring out some clever direct way to get these indices
        To do that would probably require parametrizing the bounding sphere somehow
        """
        self.get_bounding_sphere()
        return torch.where((self.L_grid - self.bounding_sphere_center).norm(dim=-1) > self.bounding_sphere_radius)

    def reaction_diffusion_dynamics(self):
        """
        This is the routine that computes the update to L and to R
        The dynamics are:
            Epithelium:
                dR/dt = Laplacian(R) + gamma*(a - R + R^2 * L)
                dL/dt = D*Laplacian(L) + gamma*(-R^2 * L)
            Mesenchyme:
                dL/dt = D*Laplacian(L) + gamma*(b - L)

        For me, the term -gamma*L in dL/dt is active everywhere EXCEPT at those gridpoints in contact with cells.
        However, the term +gamma*b is only active at those gridpoints specified by self.L_source_indices
        """
        idx = self.closest_gridpoints() # these indices correspond to the epithelium
        dL = self.dt * (self.D * self.laplacian_L_27_point() - self.gamma * self.L)
        dL[idx] += self.dt * self.gamma * ((-self.R**2) * self.L[idx])
        dL[self.L_source_indices()] += self.dt * self.gamma * self.b
        # dL += self.dt * self.gamma * self.b

        dR = self.dt * (self.laplacian_R()*0 + self.gamma *
                        (self.a - self.R + self.hill_function(self.R**2 * self.L[idx])))

        self.L += dL
        self.R += dR

    def simulation(self, potential,
                   division_decider=lambda *args: False,
                   better_WNT_gradient=False,
                   wnt_func_of_R=False,
                   beta_func_of_w=False):
        """
        Generator to implement the simulation

        Note: you can interact with this thing. Example:
        ```python
        polarguy = PolarWNT(**)
        sim = polarguy.simulation(***)
        for out in sim:
            data.append(out)
            polarguy.get_gradient_averaging()
        ```

        Parameters
        ----------
            x : torch.Tensor
                Position of each cell in 3D space
            p : torch.Tensor
                AB polarity vector of each cell
            q : torch.Tensor
                PCP vector of each cell
            lam : torch.Tensor
                weights for the terms of the potential function for each cell.
            beta : torch.Tensor
                for each cell, probability of division per unit time
            eta : float
                Strength of the added noise
            potential : callable
                function that computes the value of the potential between two cells, i and j
                call signature (x, d, dx, lam_i, lam_j, pi, pj, qi, qj)
            yield_every : int, optional
                How many simulation time steps to take between yielding the system state. Default: 1
            dt : float, optional
                Size of the time step. Default: 0.1
            kwargs : dict
                Keyword args passed to self.init_simulation and self.time_step.
                Values passed here override default values
                dt : float
                    time step
                yield_every : int
                    how many time steps to take in between yielding system state

        Yields
        ----------
            x : numpy.ndarray
                Position of each cell in 3D space
            p : numpy.ndarray
                AB polarity vector of each cell
            q : numpy.ndarray
                PCP vector of each cell
            w : numpy.ndarray
                WNT concentration at each cell
            lam : numpy.ndarray
                weights for the terms of the potential function for each cell.
        """

        tstep = 0
        while True:
            tstep += 1

            # perform cell division, depending on the output of the function division_decider
            # by default, always do cell division (this results in exponential growth of number of cells)
            # decide if cells divide this time
            division = False
            if division_decider(self, tstep):
                if self.divide_single:
                    division = self.cell_division_single()
                else:
                    division = self.cell_division()

            n_update = self.update_k(self.true_neighbour_max, tstep)
            self.k = min(self.k, len(self.x) - 1)

            # recompute potential neighbors if necessary
            if division or tstep % n_update == 0 or self.idx is None:
                self.find_potential_neighbours()

            # do the random walking of ligand particles
            # this is done _after_ cell division so the contact_counts array always has the same size as the cell position array
            self.reaction_diffusion_dynamics()

            self.get_gradient_vectors(better=better_WNT_gradient)
            self.gradient_step(tstep, potential=potential)

            if wnt_func_of_R:
                self.w = self.hill_function(self.R)
            else:
                self.w = self.w * np.exp(self.dt * self.wnt_decay)
            if beta_func_of_w:
                www = self.w.detach().clone()
                self.beta = ((www - www.min())/(www.max() - www.min())) ** self.beta_func_of_w_exponent

            if tstep % self.yield_every == 0:
                print(self.R.min(), self.R.max(),
                      (self.R.max() - self.R.min()))
                print(self.L.max(), self.L.min(), (self.L.max()-self.L.min()))
                xx = self.x.detach().to("cpu").numpy().copy()
                pp = self.p.detach().to("cpu").numpy().copy()
                qq = self.q.detach().to("cpu").numpy().copy()
                ww = self.w.detach().to("cpu").numpy().copy()
                ll = self.lam.detach().to("cpu").numpy().copy()
                lig = self.L.detach().to('cpu').numpy().copy()
                yield xx, pp, qq, ww, ll, lig

    def cell_division(self):
        """
        Decides which cells divide, and if they do, places daughter cells.
        If a cell divides, one daughter cell is placed at the same position as the parent cell, and the other is placed one cell diameter away in a uniformly random direction

        Parameters
        ----------
            x : torch.Tensor
                Position of each cell in 3D space
            p : torch.Tensor
                AB polarity vector of each cell
            q : torch.Tensor
                PCP vector of each cell
            lam : torch.Tensor
                weights for the terms of the potential function for each cell.
            beta : torch.Tensor
                for each cell, probability of division per unit time
            dt : float
                Size of the time step.
            kwargs : dict
                Valid keyword arguments:
                beta_decay : float
                    the factor by which beta (probability of cell division per unit time) decays upon cell division.
                    after cell division, one daughter cell has the same beta as the mother (b0), and the other has beta = b0 * beta_decay

        Returns
        ---------
            division : bool
                True if cell division has taken place, otherwise False
            x : torch.Tensor
                Position of each cell in 3D space
            p : torch.Tensor
                AB polarity vector of each cell
            q : torch.Tensor
                PCP vector of each cell
            lam : torch.Tensor
                weights for the terms of the potential function for each cell.
            beta : torch.Tensor
                for each cell, probability of division per unit time
        """
        if torch.sum(self.beta) < self.do_nothing_threshold:
            return False

        # set probability according to beta and dt
        d_prob = self.beta * self.dt
        # flip coins
        draw = torch.empty_like(self.beta).uniform_()
        # find successes
        events = draw < d_prob
        division = False

        if torch.sum(events) > 0:
            with torch.no_grad():
                division = True
                # find cells that will divide
                idx = torch.nonzero(events)[:, 0]

                x0 = self.x[idx, :]
                p0 = self.p[idx, :]
                q0 = self.q[idx, :]
                w0 = self.w[idx]
                R0 = self.R[idx]
                l0 = self.lam[idx, :]
                b0 = self.beta[idx] * self.beta_decay

                # make a random vector and normalize to get a random direction
                move = torch.empty_like(x0).normal_()
                move /= torch.sqrt(torch.sum(move**2, dim=1))[:, None]

                # move the cells so that the center of mass of each pair is at the same place as the mother cell was
                x0 = x0 - move/2
                self.x[idx, :] += move/2

                # divide WNT from mother cells evenly to daughter cells
                self.w[idx] /= 2
                w0 /= 2
                self.R[idx] /= 2
                R0 /= 2

                # append new cell data to the system state
                self.x = torch.cat((self.x, x0))
                self.p = torch.cat((self.p, p0))
                self.q = torch.cat((self.q, q0))
                self.w = torch.cat((self.w, w0))
                self.R = torch.cat((self.R, R0))
                self.lam = torch.cat((self.lam, l0))
                self.beta = torch.cat((self.beta, b0))

        # replenish WNT at source cell(s)
        self.w[self.wnt_cells] = 1

        self.x.requires_grad = True
        self.p.requires_grad = True
        self.q.requires_grad = True

        return division

    def cell_division_single(self):
        """
        Selects exactly one cell to divide and divides it.
        If a cell divides, one daughter cell is placed at the same position as the parent cell, and the other is placed one cell diameter away in a uniformly random direction
        """
        if torch.sum(self.beta) < self.do_nothing_threshold:
            return False

        idx = torch.multinomial(self.beta, 1)
        with torch.no_grad():
            x0 = self.x[idx, :]
            p0 = self.p[idx, :]
            q0 = self.q[idx, :]
            w0 = self.w[idx]
            R0 = self.R[idx]
            l0 = self.lam[idx, :]
            b0 = self.beta[idx] * self.beta_decay

            # make a random vector and normalize to get a random direction
            move = torch.empty_like(x0).normal_()
            move /= torch.sqrt(torch.sum(move**2, dim=1))[:, None]

            # move the cells so that the center of mass of each pair is at the same place as the mother cell was
            x0 = x0 - move/2
            self.x[idx, :] += move/2

            # divide WNT from mother cells evenly to daughter cells
            self.w[idx] /= 2
            w0 /= 2
            self.R[idx] /= 2
            R0 /= 2

            # append new cell data to the system state
            self.x = torch.cat((self.x, x0))
            self.p = torch.cat((self.p, p0))
            self.q = torch.cat((self.q, q0))
            self.w = torch.cat((self.w, w0))
            self.R = torch.cat((self.R, R0))
            self.lam = torch.cat((self.lam, l0))
            self.beta = torch.cat((self.beta, b0))

        # replenish WNT at source cell(s)
        self.w[self.wnt_cells] = 1

        self.x.requires_grad = True
        self.p.requires_grad = True
        self.q.requires_grad = True

        return True