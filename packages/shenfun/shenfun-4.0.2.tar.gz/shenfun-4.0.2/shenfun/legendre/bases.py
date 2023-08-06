r"""
Module for defining function spaces in the Legendre family.

A function is approximated in the Legendre basis as

..  math::

    u(x) = \sum_{i=0}^{N-1} \hat{u}_i L_i(x)

where :math:`L_i(x)` is the i'th Legendre polynomial of the first kind.
The Legendre polynomials are orthogonal with weight :math:`\omega=1`

.. math::

    \int_{-1}^1 L_i L_k dx = \frac{2}{2k+1} \delta_{ki}.

All other bases defined in this module are combinations of :math:`L_i`'s.
For example, a Dirichlet basis is

.. math::

    \phi_i = L_i - L_{i+2}

The basis is implemented using a stencil matrix :math:`K \in \mathbb{R}^{N-2 \times N}`,
such that

.. math::

    \boldsymbol{\phi} = K \boldsymbol{L},

where :math:`\boldsymbol{\phi}=(\phi_0, \phi_1, \ldots, \phi_{N-3})` and
:math:`\boldsymbol{L}=(L_0, L_1, \ldots, L_{N-1})`. For the Dirichlet basis
:math:`K = (\delta_{i, j} - \delta_{i+2, j})_{i,j=0}^{N-2, N}`.

The stencil matrix is used to transfer any composite basis back and forth
to the orthogonal basis.

"""

from __future__ import division
import sympy as sp
import numpy as np
from numpy.polynomial import legendre as leg
from scipy.special import eval_legendre
from mpi4py_fft import fftw
from shenfun.config import config
from shenfun.spectralbase import SpectralBase, Transform, islicedict, \
    slicedict, getCompositeBase, BoundaryConditions
from shenfun.matrixbase import SparseMatrix
from shenfun.utilities import n
from .lobatto import legendre_lobatto_nodes_and_weights
from . import fastgl


bases = ['Orthogonal',
         'ShenDirichlet',
         'ShenNeumann',
         'ShenBiharmonic',
         'ShenBiPolar',
         'LowerDirichlet',
         'NeumannDirichlet',
         'DirichletNeumann',
         'UpperDirichlet',
         'UpperDirichletNeumann',
         'BeamFixedFree',
         'Generic']
bcbases = ['BCGeneric']
testbases = ['Phi1', 'Phi2', 'Phi3', 'Phi4']
__all__ = bases + bcbases + testbases

#pylint: disable=method-hidden,no-else-return,not-callable,abstract-method,no-member,cyclic-import

try:
    import quadpy
    from mpmath import mp
    mp.dps = config['bases']['legendre']['precision']
    has_quadpy = True
except:
    has_quadpy = False
    mp = None

mode = config['bases']['legendre']['mode']
mode = mode if has_quadpy else 'numpy'

xp = sp.Symbol('x', real=True)


class Orthogonal(SpectralBase):
    r"""Function space for a regular Legendre series

    The orthogonal basis is

    .. math::

        L_k, \quad k = 0, 1, \ldots, N-1,

    where :math:`L_k` is the :math:`k`'th Legendre polynomial.

    Parameters
    ----------
    N : int
        Number of quadrature points
    quad : str, optional
        Type of quadrature

        - LG - Legendre-Gauss
        - GL - Legendre-Gauss-Lobatto
    domain : 2-tuple of numbers, optional
        The computational domain
    padding_factor : float, optional
        Factor for padding backward transforms.
    dealias_direct : bool, optional
        Set upper 1/3 of coefficients to zero before backward transform
    dtype : data-type, optional
        Type of input data in real physical space. Will be overloaded when
        basis is part of a :class:`.TensorProductSpace`.
    coordinates: 2- or 3-tuple (coordinate, position vector (, sympy assumptions)), optional
        Map for curvilinear coordinatesystem, and parameters to :class:`~shenfun.coordinates.Coordinates`

    """

    def __init__(self, N, quad="LG", domain=(-1, 1), dtype=float, padding_factor=1,
                 dealias_direct=False, coordinates=None, **kw):
        SpectralBase.__init__(self, N, quad=quad, domain=domain, dtype=dtype,
                              padding_factor=padding_factor, dealias_direct=dealias_direct,
                              coordinates=coordinates)
        self.alpha = 0
        self.beta = 0
        self.gn = 1
        self.plan(int(padding_factor*N), 0, dtype, {})

    @staticmethod
    def family():
        return 'legendre'

    def points_and_weights(self, N=None, map_true_domain=False, weighted=True, **kw):
        if N is None:
            N = self.shape(False)
        if self.quad == "LG":
            points, weights = fastgl.leggauss(N)
            #points, weights = leg.leggauss(N)

        elif self.quad == "GL":
            points, weights = legendre_lobatto_nodes_and_weights(N)
        else:
            raise NotImplementedError

        if map_true_domain is True:
            points = self.map_true_domain(points)

        return points, weights

    def mpmath_points_and_weights(self, N=None, map_true_domain=False, weighted=True, **kw):
        if mode == 'numpy' or not has_quadpy:
            return self.points_and_weights(N=N, map_true_domain=map_true_domain, weighted=weighted, **kw)
        if N is None:
            N = self.shape(False)
        if self.quad == 'LG':
            pw = quadpy.c1.gauss_legendre(N, 'mpmath')
        elif self.quad == 'GL':
            pw = quadpy.c1.gauss_lobatto(N) # No mpmath in quadpy for lobatto:-(
        points = pw.points_symbolic
        if map_true_domain is True:
            points = self.map_true_domain(points)
        return points, pw.weights_symbolic

    def vandermonde(self, x):
        return leg.legvander(x, self.shape(False)-1)

    def reference_domain(self):
        return (-1, 1)

    def plan(self, shape, axis, dtype, options):
        if shape in (0, (0,)):
            return

        if isinstance(axis, tuple):
            assert len(axis) == 1
            axis = axis[0]

        if isinstance(self.forward, Transform):
            if self.forward.input_array.shape == shape and self.axis == axis:
                # Already planned
                return

        U = fftw.aligned(shape, dtype=dtype)
        V = fftw.aligned(shape, dtype=dtype)
        U.fill(0)
        V.fill(0)
        self.axis = axis
        if self.padding_factor > 1.+1e-8:
            trunc_array = self._get_truncarray(shape, V.dtype)
            self.scalar_product = Transform(self.scalar_product, None, U, V, trunc_array)
            self.forward = Transform(self.forward, None, U, V, trunc_array)
            self.backward = Transform(self.backward, None, trunc_array, V, U)
        else:
            self.scalar_product = Transform(self.scalar_product, None, U, V, V)
            self.forward = Transform(self.forward, None, U, V, V)
            self.backward = Transform(self.backward, None, V, V, U)

        self.si = islicedict(axis=self.axis, dimensions=self.dimensions)
        self.sl = slicedict(axis=self.axis, dimensions=self.dimensions)

    def get_orthogonal(self, **kwargs):
        d = dict(quad=self.quad,
                 domain=self.domain,
                 dtype=self.dtype,
                 padding_factor=self.padding_factor,
                 dealias_direct=self.dealias_direct,
                 coordinates=self.coors.coordinates)
        d.update(kwargs)
        return Orthogonal(self.N, **d)

    def sympy_basis(self, i=0, x=xp):
        return sp.legendre(i, x)

    def L2_norm_sq(self, i):
        return 2/(2*i+1)

    def l2_norm_sq(self, i=None):
        if i is None:
            f = 2/(2*np.arange(self.N)+1)
            if self.quad == 'GL':
                f[-1] = 2/(self.N-1)
            return f
        elif i == self.N-1 and self.quad == 'GL':
            return 2/(self.N-1)
        return 2/(2*i+1)

    @staticmethod
    def bnd_values(k=0, **kw):
        from shenfun.jacobi.recursions import bnd_values
        return bnd_values(0, 0, k=k)

    def evaluate_basis(self, x, i=0, output_array=None):
        x = np.atleast_1d(x)
        if output_array is None:
            output_array = np.zeros(x.shape)
        output_array = eval_legendre(i, x, out=output_array)
        return output_array

    def evaluate_basis_all(self, x=None, argument=0):
        if x is None:
            x = self.mesh(False, False)
        return self.vandermonde(x)

    def evaluate_basis_derivative(self, x=None, i=0, k=0, output_array=None):
        if x is None:
            x = self.mesh(False, False)
        if output_array is None:
            output_array = np.zeros(x.shape)
        x = np.atleast_1d(x)
        basis = np.zeros(self.shape(True))
        basis[i] = 1
        basis = leg.Legendre(basis)
        if k > 0:
            basis = basis.deriv(k)
        output_array[:] = basis(x)
        return output_array

    def evaluate_basis_derivative_all(self, x=None, k=0, argument=0):
        if x is None:
            x = self.mesh(False, False)
        V = self.vandermonde(x)
        M = V.shape[-1]
        if k > 0:
            D = np.zeros((M, M))
            D[:-k] = leg.legder(np.eye(M, M), k)
            V = np.dot(V, D)
        return V

    def eval(self, x, u, output_array=None):
        if output_array is None:
            output_array = np.zeros(x.shape, dtype=self.dtype)
        x = self.map_reference_domain(x)
        output_array[:] = leg.legval(x, u)
        return output_array

    @property
    def is_orthogonal(self):
        return True

    @staticmethod
    def short_name():
        return 'L'

    def stencil_matrix(self, N=None):
        N = self.N if N is None else N
        return SparseMatrix({0: 1}, (N, N))

    def sympy_stencil(self, i=sp.Symbol('i', integer=True), j=sp.Symbol('j', integer=True)):
        return sp.KroneckerDelta(i, j)

    def get_recursion_matrix(self, M, N):
        k = np.arange(max(M, N))
        return SparseMatrix({-1: (k[:min(N, M-1)]+1)/(2*k[:min(N, M-1)]+1),
                             1: (k[:min(M, N-1)]+1)/(2*k[:min(M, N-1)]+3)}, shape=(M, N))

    def get_bc_basis(self):
        if self._bc_basis:
            return self._bc_basis
        self._bc_basis = BCGeneric(self.N, bc=self.bcs, domain=self.domain)
        return self._bc_basis

    def to_ortho(self, input_array, output_array=None):
        assert input_array.__class__.__name__ == 'Orthogonal'
        if output_array:
            output_array[:] = input_array
            return output_array
        return input_array

CompositeBase = getCompositeBase(Orthogonal)

class ShenDirichlet(CompositeBase):
    r"""Function space for Dirichlet boundary conditions

    The basis :math:`\{\phi_k\}_{k=0}^{N-1}` is

    .. math::

        \phi_k &= L_k - L_{k+2}, \, k=0, 1, \ldots, N-3, \\
        \phi_{N-2} &= \frac{1}{2}(L_0-L_1), \\
        \phi_{N-1} &= \frac{1}{2}(L_0+L_1),

    such that

    .. math::
        u(x) &= \sum_{k=0}^{N-1} \hat{u}_k \phi_k(x), \\
        u(-1) &= a \text{ and } u(1) = b.

    The last two bases are for boundary conditions and only used if a or b are
    different from 0. In one dimension :math:`\hat{u}_{N-2}=a` and
    :math:`\hat{u}_{N-1}=b`.

    Parameters
    ----------
    N : int
        Number of quadrature points
    quad : str, optional
        Type of quadrature

        - LG - Legendre-Gauss
        - GL - Legendre-Gauss-Lobatto

    bc : tuple of numbers
        Boundary conditions at edges of domain
    domain : 2-tuple of numbers, optional
        The computational domain
    scaled : bool, optional
        Whether or not to scale test functions with 1/sqrt(4k+6).
        Scaled test functions give a stiffness matrix equal to the
        identity matrix.
    padding_factor : float, optional
        Factor for padding backward transforms.
    dealias_direct : bool, optional
        Set upper 1/3 of coefficients to zero before backward transform
    dtype : data-type, optional
        Type of input data in real physical space. Will be overloaded when
        basis is part of a :class:`.TensorProductSpace`.
    coordinates: 2- or 3-tuple (coordinate, position vector (, sympy assumptions)), optional
        Map for curvilinear coordinatesystem, and parameters to :class:`~shenfun.coordinates.Coordinates`

    """
    def __init__(self, N, quad="LG", bc=(0, 0), domain=(-1, 1), dtype=float,
                 scaled=False, padding_factor=1, dealias_direct=False, coordinates=None, **kw):
        CompositeBase.__init__(self, N, quad=quad, domain=domain, dtype=dtype, bc=bc, scaled=scaled,
                               padding_factor=padding_factor, dealias_direct=dealias_direct,
                               coordinates=coordinates)
        self._stencil = {0: 1, 2: -1}
        if self.is_scaled():
            self._stencil = {0: 1/sp.sqrt(4*n+6), 2: -1/sp.sqrt(4*n+6)}

    @staticmethod
    def boundary_condition():
        return 'Dirichlet'

    @staticmethod
    def short_name():
        return 'SD'


class Phi1(CompositeBase):
    r"""Function space for Dirichlet boundary conditions

    The basis :math:`\{\phi_k\}_{k=0}^{N-1}` is

    .. math::

        \phi_k &= \frac{1}{2}(L_k - L_{k+2}) = \frac{(2k+3)(1-x^2)}{2(k+1)(k+2)} L'_{k+1}, \, k=0, 1, \ldots, N-3, \\
        \phi_{N-2} &= \frac{1}{2}(L_0-L_1), \\
        \phi_{N-1} &= \frac{1}{2}(L_0+L_1),

    such that

    .. math::
        u(x) &= \sum_{k=0}^{N-1} \hat{u}_k \phi_k(x), \\
        u(-1) &= a \text{ and } u(1) = b.

    The last two bases are for boundary conditions and only used if a or b are
    different from 0. In one dimension :math:`\hat{u}_{N-2}=a` and
    :math:`\hat{u}_{N-1}=b`.

    Parameters
    ----------
    N : int
        Number of quadrature points
    quad : str, optional
        Type of quadrature

        - LG - Legendre-Gauss
        - GL - Legendre-Gauss-Lobatto

    bc : tuple of numbers
        Boundary conditions at edges of domain
    domain : 2-tuple of numbers, optional
        The computational domain
    padding_factor : float, optional
        Factor for padding backward transforms.
    dealias_direct : bool, optional
        Set upper 1/3 of coefficients to zero before backward transform
    dtype : data-type, optional
        Type of input data in real physical space. Will be overloaded when
        basis is part of a :class:`.TensorProductSpace`.
    coordinates: 2- or 3-tuple (coordinate, position vector (, sympy assumptions)), optional
        Map for curvilinear coordinatesystem, and parameters to :class:`~shenfun.coordinates.Coordinates`

    """
    def __init__(self, N, quad="LG", bc=(0, 0), domain=(-1, 1), dtype=float,
                 padding_factor=1, dealias_direct=False, coordinates=None, **kw):
        CompositeBase.__init__(self, N, quad=quad, domain=domain, dtype=dtype, bc=bc,
                               padding_factor=padding_factor, dealias_direct=dealias_direct,
                               coordinates=coordinates)
        self._stencil = {0: sp.S.Half, 2: -sp.S.Half}

    @staticmethod
    def boundary_condition():
        return 'Dirichlet'

    @staticmethod
    def short_name():
        return 'P1'


class ShenNeumann(CompositeBase):
    r"""Function space for Neumann boundary conditions

    The basis :math:`\{\phi_k\}_{k=0}^{N-1}` is

    .. math::

        \phi_k &= L_{k} -  \frac{k(k+1)}{(k+2)(k+3)}L_{k+2}, \, k=0, 1, \ldots, N-3, \\
        \phi_{N-2} &= \frac{1}{6}(3L_1-L_2), \\
        \phi_{N-1} &= \frac{1}{6}(3L_1+L_2),

    such that

    .. math::
        u(x) &= \sum_{k=0}^{N-1} \hat{u}_k \phi_k(x), \\
        u'(-1) &= a \text{ and } u'(1) = b.

    The last two bases are for boundary conditions and only used if a or b are
    different from 0. In one dimension :math:`\hat{u}_{N-2}=a` and
    :math:`\hat{u}_{N-1}=b`.

    Parameters
    ----------
    N : int
        Number of quadrature points
    quad : str, optional
        Type of quadrature

        - LG - Legendre-Gauss
        - GL - Legendre-Gauss-Lobatto

    bc : 2-tuple of numbers
        Boundary conditions at edges of domain
    domain : 2-tuple of numbers, optional
        The computational domain
    padding_factor : float, optional
        Factor for padding backward transforms.
    dealias_direct : bool, optional
        Set upper 1/3 of coefficients to zero before backward transform
    dtype : data-type, optional
        Type of input data in real physical space. Will be overloaded when
        basis is part of a :class:`.TensorProductSpace`.
    coordinates: 2- or 3-tuple (coordinate, position vector (, sympy assumptions)), optional
        Map for curvilinear coordinatesystem, and parameters to :class:`~shenfun.coordinates.Coordinates`

    """
    def __init__(self, N, quad="LG", bc=(0, 0), domain=(-1, 1), padding_factor=1,
                 dealias_direct=False, dtype=float, coordinates=None, **kw):
        if isinstance(bc, (tuple, list)):
            bc = BoundaryConditions({'left': {'N': bc[0]}, 'right': {'N': bc[1]}}, domain=domain)
        CompositeBase.__init__(self, N, quad=quad, domain=domain, dtype=dtype, bc=bc,
                               padding_factor=padding_factor, dealias_direct=dealias_direct,
                               coordinates=coordinates)
        self._stencil = {0: 1, 2: -n*(n + 1)/(n**2 + 5*n + 6)}

    @staticmethod
    def boundary_condition():
        return 'Neumann'

    @staticmethod
    def short_name():
        return 'SN'


class ShenBiharmonic(CompositeBase):
    r"""Function space for biharmonic equation

    The basis :math:`\{\phi_k\}_{k=0}^{N-1}` is

    .. math::

        \phi_k &= L_n - \frac{4n+10}{2n+7}L_{n+2}+\frac{2 n + 3}{2 n + 7}L_{n+4}, \, k=0, 1, \ldots, N-5, \\
        \phi_{N-4} &= \tfrac{1}{2}L_0-\tfrac{3}{5}L_1+\tfrac{1}{10}L_3, \\
        \phi_{N-3} &= \tfrac{1}{6}L_0-\tfrac{1}{10}L_1-\tfrac{1}{6}L_2+\tfrac{1}{10}L_3, \\
        \phi_{N-2} &= \tfrac{1}{2}L_0+\tfrac{3}{5}L_1-\tfrac{1}{10}L_3), \\
        \phi_{N-1} &= -\tfrac{1}{6}L_0-\tfrac{1}{10}L_1+\tfrac{1}{6}L_2+\tfrac{1}{10}L_3,

    such that

    .. math::
        u(x) &= \sum_{k=0}^{N-1} \hat{u}_k \phi_k(x), \\
        u(-1)&=a, u'(-1) = b, u(1)=c, u'(1) = d.

    Parameters
    ----------
    N : int
        Number of quadrature points
    quad : str, optional
        Type of quadrature

        - LG - Legendre-Gauss
        - GL - Legendre-Gauss-Lobatto
    bc : 4-tuple of numbers, optional
        The values of the 4 boundary conditions at x=(-1, 1).
        The two conditions on x=-1 first, and then x=1.
        With (a, b, c, d) corresponding to
        bc = {'left': [('D', a), ('N', b)], 'right': [('D', c), ('N', d)]}
    domain : 2-tuple of numbers, optional
        The computational domain
    padding_factor : float, optional
        Factor for padding backward transforms.
    dealias_direct : bool, optional
        Set upper 1/3 of coefficients to zero before backward transform
    dtype : data-type, optional
        Type of input data in real physical space. Will be overloaded when
        basis is part of a :class:`.TensorProductSpace`.
    coordinates: 2- or 3-tuple (coordinate, position vector (, sympy assumptions)), optional
        Map for curvilinear coordinatesystem, and parameters to :class:`~shenfun.coordinates.Coordinates`

    """
    def __init__(self, N, quad="LG", bc=(0, 0, 0, 0), domain=(-1, 1), padding_factor=1,
                 dealias_direct=False, dtype=float, coordinates=None, **kw):
        CompositeBase.__init__(self, N, quad=quad, domain=domain, dtype=dtype, bc=bc,
                               padding_factor=padding_factor, dealias_direct=dealias_direct,
                               coordinates=coordinates)
        self._stencil = {0: 1, 2: -(4*n + 10)/(2*n + 7), 4: (2*n + 3)/(2*n + 7)}

    @staticmethod
    def boundary_condition():
        return 'Biharmonic'

    @staticmethod
    def short_name():
        return 'SB'


class Phi2(CompositeBase):
    r"""Function space for biharmonic equation

    The basis functions :math:`\phi_k` for :math:`k=0, 1, \ldots, N-5` are

    .. math::

        \phi_k &= \frac{(1-x^2)^2 L''_{k+2}}{h^{(2)}_{k+2}}, \\
        h^{(2)}_{k+2} &= \int_{-1}^1 L''_{k+2} L''_{k+2} (1-x^2)^2 dx, \\
               &= \frac{2 (k+1)(k+2)(k+3)(k+4)}{2k+5},

    which (along with boundary functions) becomes the basis

    .. math::

        \phi_k &= \frac{1}{2(2k+3)}\left(L_k - \frac{2(2k+5)}{2k+7}L_{k+2} + \frac{2k+3}{2k+7}L_{k+4}\right), \, k=0, 1, \ldots, N-5, \\
        \phi_{N-4} &= \tfrac{1}{2}L_0-\tfrac{3}{5}L_1+\tfrac{1}{10}L_3, \\
        \phi_{N-3} &= \tfrac{1}{6}L_0-\tfrac{1}{10}L_1-\tfrac{1}{6}L_2+\tfrac{1}{10}L_3, \\
        \phi_{N-2} &= \tfrac{1}{2}L_0+\tfrac{3}{5}L_1-\tfrac{1}{10}L_3, \\
        \phi_{N-1} &= -\tfrac{1}{6}L_0-\tfrac{1}{10}L_1+\tfrac{1}{6}L_2+\tfrac{1}{10}L_3,

    such that

    .. math::
        u(x) &= \sum_{k=0}^{N-1} \hat{u}_k \phi_k(x), \\
        u(-1)&=a, u'(-1) = b, u(1)=c, u'(1) = d.

    The last four bases are for boundary conditions and only used if a, b, c or d are
    different from 0. In one dimension :math:`\hat{u}_{N-4}=a`, :math:`\hat{u}_{N-3}=b`,
    :math:`\hat{u}_{N-2}=c` and :math:`\hat{u}_{N-1}=d`.

    Parameters
    ----------
    N : int
        Number of quadrature points
    quad : str, optional
        Type of quadrature

        - LG - Legendre-Gauss
        - GL - Legendre-Gauss-Lobatto
    bc : 4-tuple of numbers, optional
        The values of the 4 boundary conditions at x=(-1, 1).
        The two on x=-1 first and then x=1. (a, b, c, d)
    domain : 2-tuple of numbers, optional
        The computational domain
    padding_factor : float, optional
        Factor for padding backward transforms.
    dealias_direct : bool, optional
        Set upper 1/3 of coefficients to zero before backward transform
    dtype : data-type, optional
        Type of input data in real physical space. Will be overloaded when
        basis is part of a :class:`.TensorProductSpace`.
    coordinates: 2- or 3-tuple (coordinate, position vector (, sympy assumptions)), optional
        Map for curvilinear coordinatesystem, and parameters to :class:`~shenfun.coordinates.Coordinates`

    """
    def __init__(self, N, quad="LG", bc=(0, 0, 0, 0), domain=(-1, 1), padding_factor=1,
                 dealias_direct=False, dtype=float, coordinates=None, **kw):
        CompositeBase.__init__(self, N, quad=quad, domain=domain, dtype=dtype, bc=bc,
                               padding_factor=padding_factor, dealias_direct=dealias_direct,
                               coordinates=coordinates)
        self._stencil = {0: 1/(2*(2*n+3)), 2: -(2*n+5)/(2*n+7)/(2*n+3), 4: 1/(2*(2*n+7))}

    @staticmethod
    def boundary_condition():
        return 'Biharmonic'

    @staticmethod
    def short_name():
        return 'P2'


class Phi3(CompositeBase):
    r"""Function space for 6th order equations

    The basis functions :math:`\phi_k` for :math:`k=0, 1, \ldots, N-7` are

    .. math::
        \phi_k &= \frac{(1-x^2)^3}{h^{(3)}_{k+3}} L^{(3)}_{k+3}}, \, k=0, 1, \ldots, N-7, \\
        h^{(3)}_{k+3} &= \frac{2\Gamma(k+7)}{\Gamma(k+1)(2k+7)} = \int_{-1}^1 L^{(3)}_{k+3} L^{(3)}_{k+3}(1-x^2)^3 dx,

    where :math:`L^{(3)}_k` is the 3'rd derivative of :math:`L_k`.
    The 6 boundary basis functions are computed using :func:`.jacobi.findbasis.get_bc_basis`,
    but they are too messy to print here. We have

    .. math::
        u(x) &= \sum_{k=0}^{N-1} \hat{u}_k \phi_k(x), \\
        u(-1) &= a, u'(-1)=b, u''(-1)=c, u(1)=d u'(1)=e, u''(1)=f.

    The last 6 basis functions are for boundary conditions and only used if there
    are nonzero boundary conditions.

    Parameters
    ----------
    N : int
        Number of quadrature points
    quad : str, optional
        Type of quadrature
        - LG - Legendre-Gauss
        - GL - Legendre-Gauss-Lobatto
    bc : 6-tuple of numbers, optional
        Boundary conditions.
    domain : 2-tuple of numbers, optional
        The computational domain
    padding_factor : float, optional
        Factor for padding backward transforms.
    dealias_direct : bool, optional
        Set upper 1/3 of coefficients to zero before backward transform
    dtype : data-type, optional
        Type of input data in real physical space. Will be overloaded when
        basis is part of a :class:`.TensorProductSpace`.
    coordinates: 2- or 3-tuple (coordinate, position vector (, sympy assumptions)), optional
        Map for curvilinear coordinatesystem, and parameters to :class:`~shenfun.coordinates.Coordinates`
    """
    def __init__(self, N, quad="LG", bc=(0,)*6, domain=(-1, 1), dtype=float,
                 padding_factor=1, dealias_direct=False, coordinates=None, **kw):
        CompositeBase.__init__(self, N, quad=quad, domain=domain, dtype=dtype, bc=bc,
                               padding_factor=padding_factor, dealias_direct=dealias_direct,
                               coordinates=coordinates)
        #self._stencil = {
        #    0: sp.simplify(matpow(b, 3, 0, 0, n+3, n) / h(0, 0, n, 0)),
        #    2: sp.simplify(matpow(b, 3, 0, 0, n+3, n+2) / h(0, 0, n+2, 0)),
        #    4: sp.simplify(matpow(b, 3, 0, 0, n+3, n+4) / h(0, 0, n+4, 0)),
        #    6: sp.simplify(matpow(b, 3, 0, 0, n+3, n+6) / h(0, 0, n+6, 0))}
        self._stencil = {
            0: 1/(2*(4*n**2 + 16*n + 15)),
            2: -3/(8*n**2 + 48*n + 54),
            4: 3/(2*(4*n**2 + 32*n + 55)),
            6: -1/(8*n**2 + 80*n + 198)
        }

    @staticmethod
    def boundary_condition():
        return '6th order'

    @staticmethod
    def short_name():
        return 'P3'


class Phi4(CompositeBase):
    r"""Function space with 2 Dirichlet and 6 Neumann boundary conditions

    The basis functions :math:`\phi_k` for :math:`k=0, 1, \ldots, N-9` are

    .. math::

        \phi_k &= \frac{(1-x^2)^4}{h^{(4)}_{k+4}} L^{(4)}_{k+4}, \\
        h^{(4)}_{k+4} &= \frac{2\Gamma(k+9)}{\Gamma(k+1)(2k+9)} = \int_{-1}^1 L^{(4)}_{k+4} L^{(4)}_{k+4} (1-x^2)^4 dx,

    where :math:`L^{(4)}_k` is the 4'th derivative of :math:`L_k`.
    The boundary basis for inhomogeneous boundary conditions is too
    messy to print, but can be obtained using :func:`~shenfun.utilities.findbasis.get_bc_basis`.
    We have

    .. math::
        u(x) &= \sum_{k=0}^{N-1} \hat{u}_k \phi_k(x), \\
        u(-1) &= a, u'(-1)=b, u''(-1)=c, u'''(-1)=d, u(1)=e u'(1)=f, u''(1)=g, u'''(1)=h.

    The last 8 basis functions are for boundary conditions and only used if there
    are nonzero boundary conditions.

    Parameters
    ----------
    N : int, optional
        Number of quadrature points
    quad : str, optional
        Type of quadrature
        - LG - Legendre-Gauss
        - GL - Legendre-Gauss-Lobatto
    bc : 8-tuple of numbers
    domain : 2-tuple of numbers, optional
        The computational domain
    dtype : data-type, optional
        Type of input data in real physical space. Will be overloaded when
        basis is part of a :class:`.TensorProductSpace`.
    padding_factor : float, optional
        Factor for padding backward transforms.
    dealias_direct : bool, optional
        Set upper 1/3 of coefficients to zero before backward transform
    coordinates: 2- or 3-tuple (coordinate, position vector (, sympy assumptions)), optional
        Map for curvilinear coordinatesystem, and parameters to :class:`~shenfun.coordinates.Coordinates`

    """
    def __init__(self, N, quad="LG", bc=(0,)*8, domain=(-1, 1), dtype=float,
                 padding_factor=1, dealias_direct=False, coordinates=None, **kw):
        CompositeBase.__init__(self, N, quad=quad, domain=domain, dtype=dtype, bc=bc,
                               padding_factor=padding_factor, dealias_direct=dealias_direct,
                               coordinates=coordinates)
        #self._stencil = {
        #   0: sp.simplify(matpow(b, 4, 0, 0, n+4, n) / h(0, 0, n, 0)),
        #   2: sp.simplify(matpow(b, 4, 0, 0, n+4, n+2) / h(0, 0, n+2, 0)),
        #   4: sp.simplify(matpow(b, 4, 0, 0, n+4, n+4) / h(0, 0, n+4, 0)),
        #   6: sp.simplify(matpow(b, 4, 0, 0, n+4, n+6) / h(0, 0, n+6, 0)),
        #   8: sp.simplify(matpow(b, 4, 0, 0, n+4, n+8) / h(0, 0, n+8, 0))}
        # Below are the same but faster since already simplified
        self._stencil = {
            0: 1/(2*(8*n**3 + 60*n**2 + 142*n + 105)),
            2: -2/(8*n**3 + 84*n**2 + 262*n + 231),
            4: 3*(2*n + 9)/((2*n + 5)*(2*n + 7)*(2*n + 11)*(2*n + 13)),
            6: -2/(8*n**3 + 132*n**2 + 694*n + 1155),
            8: 1/(2*(8*n**3 + 156*n**2 + 1006*n + 2145))
        }

    @staticmethod
    def boundary_condition():
        return 'Biharmonic*2'

    @staticmethod
    def short_name():
        return 'P4'


class BeamFixedFree(CompositeBase):
    r"""Function space for fixed free beams

    The basis :math:`\{\phi_k\}_{k=0}^{N-1}` is

    .. math::

        \phi_k &= L_k + a_kL_{k+1} + b_k L_{k+2} + c_k L_{k+3} + d_k L_{k+4} , \, k=0, 1, \ldots, N-5, \\
        \phi_{N-4} &= \tfrac{1}{2}L_0-\tfrac{3}{5}L_1+\tfrac{1}{10}L_3, \\
        \phi_{N-3} &= \tfrac{1}{6}L_0-\tfrac{1}{10}L_1-\tfrac{1}{6}L_2+\tfrac{1}{10}L_3, \\
        \phi_{N-2} &= \tfrac{1}{2}L_0+\tfrac{3}{5}L_1-\tfrac{1}{10}L_3), \\
        \phi_{N-1} &= -\tfrac{1}{6}L_0-\tfrac{1}{10}L_1+\tfrac{1}{6}L_2+\tfrac{1}{10}L_3,

    where

    .. math::

        a_k &= \frac{4 \left(2 n + 3\right)}{\left(n + 3\right)^{2}}, \\
        b_k &= -\frac{2 \left(n - 1\right) \left(n + 1\right) \left(n + 6\right) \left(2 n + 5\right)}{\left(n + 3\right)^{2} \left(n + 4\right) \left(2 n + 7\right)}, \\
        c_k &= -\frac{4 \left(n + 1\right)^{2} \left(2 n + 3\right)}{\left(n + 3\right)^{2} \left(n + 4\right)^{2}}, \\
        d_k &= \frac{\left(n + 1\right)^{2} \left(n + 2\right)^{2} \left(2 n + 3\right)}{\left(n + 3\right)^{2} \left(n + 4\right)^{2} \left(2 n + 7\right)}.

    We have

    .. math::
        u(x) &= \sum_{k=0}^{N-1} \hat{u}_k \phi_k(x), \\
        u(-1)&=a, u'(-1) = b, u''(1)=c, u'''(1) = d.

    The last four bases are for boundary conditions and only used if a, b, c or d are
    different from 0. In one dimension :math:`\hat{u}_{N-4}=a`, :math:`\hat{u}_{N-3}=b`,
    :math:`\hat{u}_{N-2}=c` and :math:`\hat{u}_{N-1}=d`.

    Parameters
    ----------
    N : int
        Number of quadrature points
    quad : str, optional
        Type of quadrature

        - LG - Legendre-Gauss
        - GL - Legendre-Gauss-Lobatto
    4-tuple of numbers, optional
        The values of the 4 boundary conditions
        u(-1) = a, u'(-1) = b, u''(1) = c, u'''(1) = d

    domain : 2-tuple of numbers, optional
        The computational domain
    padding_factor : float, optional
        Factor for padding backward transforms.
    dealias_direct : bool, optional
        Set upper 1/3 of coefficients to zero before backward transform
    dtype : data-type, optional
        Type of input data in real physical space. Will be overloaded when
        basis is part of a :class:`.TensorProductSpace`.
    coordinates: 2- or 3-tuple (coordinate, position vector (, sympy assumptions)), optional
        Map for curvilinear coordinatesystem, and parameters to :class:`~shenfun.coordinates.Coordinates`

    """
    def __init__(self, N, quad="LG", bc=(0, 0, 0, 0), domain=(-1, 1), padding_factor=1,
                 dealias_direct=False, dtype=float, coordinates=None, **kw):
        if isinstance(bc, (tuple, list)):
            bc = BoundaryConditions({'left': {'D': bc[0], 'N': bc[1]}, 'right': {'N2': bc[2], 'N3': bc[3]}}, domain=domain)
        CompositeBase.__init__(self, N, quad=quad, domain=domain, dtype=dtype, bc=bc,
                               padding_factor=padding_factor, dealias_direct=dealias_direct,
                               coordinates=coordinates)
        self._stencil = {
            0: 1,
            1: 4*(2*n + 3)/(n**2 + 6*n + 9),
            2: 2*(-2*n**4 - 17*n**3 - 28*n**2 + 17*n + 30)/(2*n**4 + 27*n**3 + 136*n**2 + 303*n + 252),
            3: -(8*n**3 + 28*n**2 + 32*n + 12)/(n**4 + 14*n**3 + 73*n**2 + 168*n + 144),
            4: (2*n**5 + 15*n**4 + 44*n**3 + 63*n**2 + 44*n + 12)/(2*n**5 + 35*n**4 + 244*n**3 + 847*n**2 + 1464*n + 1008)
        }

    @staticmethod
    def boundary_condition():
        return 'BeamFixedFree'

    @staticmethod
    def short_name():
        return 'BF'


class UpperDirichlet(CompositeBase):
    r"""Function space with single Dirichlet on upper edge

    The basis :math:`\{\phi_k\}_{k=0}^{N-1}` is

    .. math::

        \phi_k &= L_{k} - L_{k+1}, \, k=0, 1, \ldots, N-2, \\
        \phi_{N-1} &= L_0,

    such that

    .. math::
        u(x) &= \sum_{k=0}^{N-1} \hat{u}_k \phi_k(x), \\
        u(1) &= a.

    The last basis function is for boundary condition and only used if a is
    different from 0. In one dimension :math:`\hat{u}_{N-1}=a`.

    Parameters
    ----------
    N : int
        Number of quadrature points
    quad : str, optional
        Type of quadrature

        - LG - Legendre-Gauss
        - GL - Legendre-Gauss-Lobatto
    bc : 2-tuple of (None, number), optional
        The number is the boundary condition value
    domain : 2-tuple of numbers, optional
        The computational domain
    padding_factor : float, optional
        Factor for padding backward transforms.
    dealias_direct : bool, optional
        Set upper 1/3 of coefficients to zero before backward transform
    dtype : data-type, optional
        Type of input data in real physical space. Will be overloaded when
        basis is part of a :class:`.TensorProductSpace`.
    coordinates: 2- or 3-tuple (coordinate, position vector (, sympy assumptions)), optional
        Map for curvilinear coordinatesystem, and parameters to :class:`~shenfun.coordinates.Coordinates`

    """
    def __init__(self, N, quad="LG", bc=(None, 0), domain=(-1, 1), dtype=float,
                 padding_factor=1, dealias_direct=False, coordinates=None, **kw):
        CompositeBase.__init__(self, N, quad=quad, domain=domain, dtype=dtype, bc=bc,
                               padding_factor=padding_factor, dealias_direct=dealias_direct,
                               coordinates=coordinates)
        self._stencil = {0: 1, 1: -1}

    @staticmethod
    def boundary_condition():
        return 'UpperDirichlet'

    @staticmethod
    def short_name():
        return 'UD'


class ShenBiPolar(CompositeBase):
    r"""Function space for the Biharmonic equation

    The basis :math:`\{\phi_k\}_{k=0}^{N-1}` is

    .. math::

        \phi_k &= (1-x^2)^2 L'_{k+1}, \quad k=0,1, \ldots, N-5, \\
        \phi_{N-4} &= \tfrac{1}{2}L_0-\tfrac{3}{5}L_1+\tfrac{1}{10}L_3, \\
        \phi_{N-3} &= \tfrac{1}{6}L_0-\tfrac{1}{10}L_1-\tfrac{1}{6}L_2+\tfrac{1}{10}L_3, \\
        \phi_{N-2} &= \tfrac{1}{2}L_0+\tfrac{3}{5}L_1-\tfrac{1}{10}L_3), \\
        \phi_{N-1} &= -\tfrac{1}{6}L_0-\tfrac{1}{10}L_1+\tfrac{1}{6}L_2+\tfrac{1}{10}L_3,

    such that

    .. math::
        u(x) &= \sum_{k=0}^{N-1} \hat{u}_k \phi_k(x), \\
        u(-1)&=a, u'(-1) = b, u(1)=c, u'(1) = d.

    The last four bases are for boundary conditions and only used if a, b, c or d are
    different from 0. In one dimension :math:`\hat{u}_{N-4}=a`, :math:`\hat{u}_{N-3}=b`,
    :math:`\hat{u}_{N-2}=c` and :math:`\hat{u}_{N-1}=d`.

    Parameters
    ----------
    N : int
        Number of quadrature points
    quad : str, optional
        Type of quadrature

        - LG - Legendre-Gauss
        - GL - Legendre-Gauss-Lobatto
    bc : 4-tuple of numbers, optional
        The values of the 4 boundary conditions at x=(-1, 1).
        The two on x=-1 first and then x=1. (a, b, c, d)
    domain : 2-tuple of numbers, optional
        The computational domain
    padding_factor : float, optional
        Factor for padding backward transforms.
    dealias_direct : bool, optional
        Set upper 1/3 of coefficients to zero before backward transform
    dtype : data-type, optional
        Type of input data in real physical space. Will be overloaded when
        basis is part of a :class:`.TensorProductSpace`.
    coordinates: 2- or 3-tuple (coordinate, position vector (, sympy assumptions)), optional
        Map for curvilinear coordinatesystem, and parameters to :class:`~shenfun.coordinates.Coordinates`

    """
    def __init__(self, N, quad="LG", domain=(-1, 1), bc=(0, 0, 0, 0), dtype=float,
                 padding_factor=1, dealias_direct=False, coordinates=None, **kw):
        CompositeBase.__init__(self, N, quad=quad, domain=domain, dtype=dtype, bc=bc,
                               padding_factor=padding_factor, dealias_direct=dealias_direct,
                               coordinates=coordinates)

    @staticmethod
    def boundary_condition():
        return 'Biharmonic'

    @staticmethod
    def short_name():
        return 'SP'

    def sympy_stencil(self, i=sp.Symbol('i', integer=True), j=sp.Symbol('j', integer=True)):
        return RuntimeError, "Not possible for current basis"

    def stencil_matrix(self, N=None):
        N = self.N if N is None else N
        k = np.arange(N)
        ak = k*(k-1)/(2*k-1)/(2*k+1)
        bk = -2*(k**2+k-1)/(2*k-1)/(2*k+3)
        ck = (k+1)*(k+2)/(2*k+1)/(2*k+3)
        d = np.zeros(N)
        d[:-4] = (k[:-4]+1)*(k[:-4]+2)/(2*k[:-4]+3)*(ak[2:-2]-bk[:-4])
        d[0] = 8/15
        d[1] = 24/35
        dm2 = np.zeros(N-2)
        dm2[:-4] = -(k[2:-4]+1)*(k[2:-4]+2)/(2*k[2:-4]+3)*ak[2:-4]
        dp2 = np.zeros(N-2)
        dp2[:-2] = (k[:-4]+1)*(k[:-4]+2)/(2*k[:-4]+3)*(bk[2:-2]-ck[:-4])
        dp2[0] = -16/21
        dp2[1] = -16/15
        dp4 = np.zeros(N-4)
        dp4[:] = (k[:-4]+1)*(k[:-4]+2)/(2*k[:-4]+3)*ck[2:-2]
        dp4[0] = 8/35
        dp4[1] = 8/21
        return SparseMatrix({-2: dm2, 0: d, 2: dp2, 4: dp4}, (N, N))

class DirichletNeumann(CompositeBase):
    r"""Function space for mixed Dirichlet/Neumann boundary conditions

    The basis :math:`\{\phi_k\}_{k=0}^{N-1}` is

    .. math::

        \phi_k &= L_{k} + \frac{2n+3}{\left(n+2\right)^{2}}L_{k+1} - \frac{\left(n+1\right)^{2}}{\left(n+2\right)^{2}} L_{k+2}, \, k=0, 1, \ldots, N-3, \\
        \phi_{N-2} &= L_0, \\
        \phi_{N-1} &= L_0+L_1,

    such that

    .. math::
        u(x) &= \sum_{k=0}^{N-1} \hat{u}_k \phi_k(x), \\
        u(-1) &= a, u'(1)=b.

    The last two bases are for boundary conditions and only used if a or b are
    different from 0. In one dimension :math:`\hat{u}_{N-2}=a` and
    :math:`\hat{u}_{N-1}=b`.

    Parameters
    ----------
    N : int
        Number of quadrature points
    quad : str, optional
        Type of quadrature

        - LG - Legendre-Gauss
        - GL - Legendre-Gauss-Lobatto

    bc : tuple of numbers
        Boundary conditions at edges of domain. Dirichlet first.
    domain : 2-tuple of numbers, optional
        The computational domain
    padding_factor : float, optional
        Factor for padding backward transforms.
    dealias_direct : bool, optional
        Set upper 1/3 of coefficients to zero before backward transform
    dtype : data-type, optional
        Type of input data in real physical space. Will be overloaded when
        basis is part of a :class:`.TensorProductSpace`.
    coordinates: 2- or 3-tuple (coordinate, position vector (, sympy assumptions)), optional
        Map for curvilinear coordinatesystem, and parameters to :class:`~shenfun.coordinates.Coordinates`

    """
    def __init__(self, N, quad="LG", bc=(0, 0), domain=(-1, 1), dtype=float,
                 padding_factor=1, dealias_direct=False, coordinates=None, **kw):
        if isinstance(bc, (tuple, list)):
            bc = BoundaryConditions({'left': {'D': bc[0]}, 'right': {'N': bc[1]}}, domain=domain)
        CompositeBase.__init__(self, N, quad=quad, domain=domain, dtype=dtype, bc=bc,
                               padding_factor=padding_factor, dealias_direct=dealias_direct,
                               coordinates=coordinates)
        self._stencil = {0: 1, 1: (2*n + 3)/(n**2 + 4*n + 4), 2: -(n**2 + 2*n + 1)/(n**2 + 4*n + 4)}

    @staticmethod
    def boundary_condition():
        return 'DirichletNeumann'

    @staticmethod
    def short_name():
        return 'DN'


class LowerDirichlet(CompositeBase):
    r"""Function space with single Dirichlet boundary condition

    The basis :math:`\{\phi_k\}_{k=0}^{N-1}` is

    .. math::

        \phi_k &= L_{k} + L_{k+1}, \, k=0, 1, \ldots, N-2, \\
        \phi_{N-1} &= L_0,

    such that

    .. math::
        u(x) &= \sum_{k=0}^{N-1} \hat{u}_k \phi_k(x), \\
        u(-1) &= a.

    The last basis function is for boundary condition and only used if a is
    different from 0. In one dimension :math:`\hat{u}_{N-1}=a`.

    Parameters
    ----------
    N : int
        Number of quadrature points
    quad : str, optional
        Type of quadrature

        - LG - Legendre-Gauss
        - GL - Legendre-Gauss-Lobatto

    bc : tuple of (number, None)
        Boundary conditions at edges of domain.
    domain : 2-tuple of numbers, optional
        The computational domain
    padding_factor : float, optional
        Factor for padding backward transforms.
    dealias_direct : bool, optional
        Set upper 1/3 of coefficients to zero before backward transform
    dtype : data-type, optional
        Type of input data in real physical space. Will be overloaded when
        basis is part of a :class:`.TensorProductSpace`.
    coordinates: 2- or 3-tuple (coordinate, position vector (, sympy assumptions)), optional
        Map for curvilinear coordinatesystem, and parameters to :class:`~shenfun.coordinates.Coordinates`

    """
    def __init__(self, N, quad="LG", bc=(0, None), domain=(-1, 1), dtype=float,
                 padding_factor=1, dealias_direct=False, coordinates=None, **kw):
        CompositeBase.__init__(self, N, quad=quad, domain=domain, dtype=dtype, bc=bc,
                               padding_factor=padding_factor, dealias_direct=dealias_direct,
                               coordinates=coordinates)
        self._stencil = {0: 1, 1: 1}

    @staticmethod
    def boundary_condition():
        return 'LowerDirichlet'

    @staticmethod
    def short_name():
        return 'LD'


class NeumannDirichlet(CompositeBase):
    r"""Function space for mixed Neumann/Dirichlet boundary conditions

    The basis :math:`\{\phi_k\}_{k=0}^{N-1}` is

    .. math::

        \phi_k &= L_{k} - \frac{2n+3}{\left(n+2\right)^{2}}L_{k+1} - \frac{\left(n+1\right)^{2}}{\left(n+2\right)^{2}}L_{k+2}, \, k=0, 1, \ldots, N-3, \\
        \phi_{N-2} &= -L_0+L_1, \\
        \phi_{N-1} &= L_0,

    such that

    .. math::
        u(x) &= \sum_{k=0}^{N-1} \hat{u}_k \phi_k(x), \\
        u'(-1) &= a, u(1)=b.

    The last two bases are for boundary conditions and only used if a or b are
    different from 0. In one dimension :math:`\hat{u}_{N-2}=a` and
    :math:`\hat{u}_{N-1}=b`.

    Parameters
    ----------
    N : int
        Number of quadrature points
    quad : str, optional
        Type of quadrature

        - LG - Legendre-Gauss
        - GL - Legendre-Gauss-Lobatto

    bc : tuple of numbers
        Boundary conditions at edges of domain. Neumann first.
    domain : 2-tuple of numbers, optional
        The computational domain
    padding_factor : float, optional
        Factor for padding backward transforms.
    dealias_direct : bool, optional
        Set upper 1/3 of coefficients to zero before backward transform
    dtype : data-type, optional
        Type of input data in real physical space. Will be overloaded when
        basis is part of a :class:`.TensorProductSpace`.
    coordinates: 2- or 3-tuple (coordinate, position vector (, sympy assumptions)), optional
        Map for curvilinear coordinatesystem, and parameters to :class:`~shenfun.coordinates.Coordinates`

    """
    def __init__(self, N, quad="LG", bc=(0, 0), domain=(-1, 1), dtype=float,
                 padding_factor=1, dealias_direct=False, coordinates=None, **kw):
        if isinstance(bc, (tuple, list)):
            bc = BoundaryConditions({'left': {'N': bc[0]}, 'right': {'D': bc[1]}}, domain=domain)
        CompositeBase.__init__(self, N, quad=quad, domain=domain, dtype=dtype, bc=bc,
                               padding_factor=padding_factor, dealias_direct=dealias_direct,
                               coordinates=coordinates)
        self._stencil = {0: 1, 1: -(2*n + 3)/(n**2 + 4*n + 4), 2: -(n**2 + 2*n + 1)/(n**2 + 4*n + 4)}

    @staticmethod
    def boundary_condition():
        return 'NeumannDirichlet'

    @staticmethod
    def short_name():
        return 'ND'


class UpperDirichletNeumann(CompositeBase):
    r"""Function space for both Dirichlet and Neumann boundary conditions
    on the right hand side.

    The basis :math:`\{\phi_k\}_{k=0}^{N-1}` is

    .. math::

        \phi_k &= L_{k} - \frac{2k+3}{k+2}L_{k+1} + \frac{k+1}{k+2}L_{k+2}, \, k=0, 1, \ldots, N-3, \\
        \phi_{N-2} &= L_0, \\
        \phi_{N-1} &= -L_0+L_1,

    such that

    .. math::
        u(x) &= \sum_{k=0}^{N-1} \hat{u}_k \phi_k(x), \\
        u(1) &= a, u'(1)=b.

    The last two bases are for boundary conditions and only used if a or b are
    different from 0. In one dimension :math:`\hat{u}_{N-2}=a` and
    :math:`\hat{u}_{N-1}=b`.

    Parameters
    ----------
    N : int
        Number of quadrature points
    quad : str, optional
        Type of quadrature

        - LG - Legendre-Gauss
        - GL - Legendre-Gauss-Lobatto

    bc : tuple of numbers
        Boundary conditions at edges of domain, Dirichlet first.
    domain : 2-tuple of numbers, optional
        The computational domain
    padding_factor : float, optional
        Factor for padding backward transforms.
    dealias_direct : bool, optional
        Set upper 1/3 of coefficients to zero before backward transform
    dtype : data-type, optional
        Type of input data in real physical space. Will be overloaded when
        basis is part of a :class:`.TensorProductSpace`.
    coordinates: 2- or 3-tuple (coordinate, position vector (, sympy assumptions)), optional
        Map for curvilinear coordinatesystem, and parameters to :class:`~shenfun.coordinates.Coordinates`

    Note
    ----
    This basis is not recommended as it leads to a poorly conditioned
    stiffness matrix.
    """
    def __init__(self, N, quad="LG", bc=(0, 0), domain=(-1, 1), dtype=float,
                 padding_factor=1, dealias_direct=False, coordinates=None, **kw):
        if isinstance(bc, (tuple, list)):
            bc = BoundaryConditions({'right': {'D': bc[0], 'N': bc[1]}}, domain=domain)
        CompositeBase.__init__(self, N, quad=quad, domain=domain, dtype=dtype, bc=bc,
                               padding_factor=padding_factor, dealias_direct=dealias_direct,
                               coordinates=coordinates)
        self._stencil = {0: 1, 1: -(2*n + 3)/(n + 2), 2: (n + 1)/(n + 2)}

    @staticmethod
    def boundary_condition():
        return 'UpperDirichletNeumann'

    @staticmethod
    def short_name():
        return 'UDN'


class Generic(CompositeBase):
    r"""Function space for space with any boundary conditions

    Any combination of Dirichlet and Neumann is possible.

    Parameters
    ----------
    N : int, optional
        Number of quadrature points
    quad : str, optional
        Type of quadrature

        - LG - Legendre-Gauss
        - GL - Legendre-Gauss-Lobatto

    bc : dict, optional
        The dictionary must have keys 'left' and 'right', to describe boundary
        conditions on the left and right boundaries. Specify Dirichlet on both
        ends with

            {'left': {'D': a}, 'right': {'D': b}}

        for some values `a` and `b`, that will be neglected in the current
        function. Specify mixed Neumann and Dirichlet as

            {'left': {'N': a}, 'right': {'N': b}}

        For both conditions on the right do

            {'right': {'N': a, 'D': b}}

        Any combination should be possible, and it should also be possible to
        use second derivatives `N2`. See :class:`~shenfun.spectralbase.BoundaryConditions`.
    domain : 2-tuple of numbers, optional
        The computational domain
    dtype : data-type, optional
        Type of input data in real physical space. Will be overloaded when
        basis is part of a :class:`.TensorProductSpace`.
    padding_factor : float, optional
        Factor for padding backward transforms.
    dealias_direct : bool, optional
        Set upper 1/3 of coefficients to zero before backward transform
    coordinates: 2- or 3-tuple (coordinate, position vector (, sympy assumptions)), optional
        Map for curvilinear coordinatesystem, and parameters to :class:`~shenfun.coordinates.Coordinates`

    Note
    ----
    A test function is always using homogeneous boundary conditions.

    """
    def __init__(self, N, quad="LG", bc={}, domain=(-1, 1), dtype=float,
                 padding_factor=1, dealias_direct=False, coordinates=None, **kw):
        if not isinstance(bc, BoundaryConditions):
            bc = BoundaryConditions(bc, domain=domain)
        CompositeBase.__init__(self, N, quad=quad, domain=domain, dtype=dtype, bc=bc,
                               padding_factor=padding_factor, dealias_direct=dealias_direct,
                               coordinates=coordinates)

    @staticmethod
    def boundary_condition():
        return 'Generic'

    @staticmethod
    def short_name():
        return 'GL'


class BCBase(CompositeBase):
    """Function space for inhomogeneous boundary conditions

    Parameters
    ----------
    N : int
        Number of quadrature points in the homogeneous space.
    bc : dict
        The boundary conditions in dictionary form, see
        :class:`.BoundaryConditions`.
    domain : 2-tuple of numbers, optional
        The domain of the homogeneous space.

    """

    def __init__(self, N, bc=None, domain=(-1, 1), **kw):
        CompositeBase.__init__(self, N, bc=bc, domain=domain)
        self._stencil_matrix = None

    def stencil_matrix(self, N=None):
        raise NotImplementedError

    @staticmethod
    def short_name():
        raise NotImplementedError

    @staticmethod
    def boundary_condition():
        return 'Apply'

    @property
    def is_boundary_basis(self):
        return True

    def shape(self, forward_output=True):
        if forward_output:
            return self.stencil_matrix().shape[0]
        else:
            return self.N

    @property
    def dim_ortho(self):
        return self.stencil_matrix().shape[1]

    def slice(self):
        return slice(self.N-self.shape(), self.N)

    def vandermonde(self, x):
        return leg.legvander(x, self.dim_ortho-1)

    def _composite(self, V, argument=1):
        N = self.shape()
        P = np.zeros(V[:, :N].shape)
        P[:] = np.tensordot(V[:, :self.dim_ortho], self.stencil_matrix(), (1, 1))
        return P

    def sympy_basis(self, i=0, x=xp):
        M = self.stencil_matrix()
        return np.sum(M[i]*np.array([sp.legendre(j, x) for j in range(self.dim_ortho)]))

    def evaluate_basis(self, x, i=0, output_array=None):
        x = np.atleast_1d(x)
        if output_array is None:
            output_array = np.zeros(x.shape)
        V = self.vandermonde(x)
        output_array[:] = np.dot(V, self.stencil_matrix()[i])
        return output_array

    def evaluate_basis_derivative(self, x=None, i=0, k=0, output_array=None):
        output_array = SpectralBase.evaluate_basis_derivative(self, x=x, i=i, k=k, output_array=output_array)
        return output_array

    def to_ortho(self, input_array, output_array=None):
        from shenfun import Function
        T = self.get_orthogonal()
        if output_array is None:
            output_array = Function(T)
        else:
            output_array.fill(0)
        M = self.stencil_matrix().T
        for k, row in enumerate(M):
            output_array[k] = np.dot(row, input_array)
        return output_array

    def eval(self, x, u, output_array=None):
        v = self.to_ortho(u)
        output_array = v.eval(x, output_array=output_array)
        return output_array

    def get_orthogonal(self, **kwargs):
        d = dict(quad=self.quad,
                 domain=self.domain,
                 dtype=self.dtype)
        d.update(kwargs)
        return Orthogonal(self.dim_ortho, **d)

class BCGeneric(BCBase):

    @staticmethod
    def short_name():
        return 'BG'

    def stencil_matrix(self, N=None):
        if self._stencil_matrix is None:
            from shenfun.utilities.findbasis import get_bc_basis
            self._stencil_matrix = np.array(get_bc_basis(self.bcs, 'legendre'))
        return self._stencil_matrix
