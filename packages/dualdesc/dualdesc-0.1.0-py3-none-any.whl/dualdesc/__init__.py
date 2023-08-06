from typing import Optional, Union, Any, Tuple, List
from typing_extensions import Literal

import numpy as np
import cdd

CDDNumberType = Union[Literal['float'], Literal['fraction']]
NDArray = Any
DType = Any

class HRepr:
	"""
		A polytope defined as an intersection of half-spaces (H-representation).
		> { x | Au @ x <= bu; Ae @ x = be }
	"""
	
	dim: int
	dtype: DType
	
	# Inequalities ([u]pper-bounds): Au @ x <= bu
	Au: NDArray
	bu: NDArray
	# Equalities: Ae @ x = be
	Ae: NDArray
	be: NDArray
	
	def __init__(
		self,
		Au: Optional[NDArray] = None,
		bu: Optional[NDArray] = None,
		Ae: Optional[NDArray] = None,
		be: Optional[NDArray] = None,
	) -> None:
		assert (Au is None) == (bu is None)
		assert (Ae is None) == (be is None)
		A = _first_not_None(Au, Ae)
		assert A is not None
		
		self.dim = A.shape[1]
		self.dtype = A.dtype
		
		if Au is None:
			Au = np.empty((0, self.dim), dtype = A.dtype)
		if bu is None:
			bu = np.empty(0, dtype = A.dtype)
		if Ae is None:
			Ae = np.empty((0, self.dim), dtype = A.dtype)
		if be is None:
			be = np.empty(0, dtype = A.dtype)
		
		self.Au = Au
		self.bu = bu
		self.Ae = Ae
		self.be = be
	
	@classmethod
	def intersect(cls, *hs: 'HRepr') -> 'HRepr':
		Au = []
		bu = []
		Ae = []
		be = []
		for h in hs:
			Au.append(h.Au)
			bu.append(h.bu)
			Ae.append(h.Ae)
			be.append(h.be)
		return cls(
			_concat(Au, axis = 0),
			_concat(bu, axis = 0),
			_concat(Ae, axis = 0),
			_concat(be, axis = 0),
		)
	
	def to_inequalities(self) -> Tuple[NDArray, NDArray]:
		"""
			Consolidate into only inequalities:
			> { x | A @ x <= b }
		"""
		A = self.Au
		b = self.bu
		if len(self.Ae) > 0:
			A = _concat([A, self.Ae, -self.Ae], axis = 0)
			b = _concat([b, self.be, -self.be], axis = 0)
		return A, b
	
	def to_cdd_polyhedron(self, *, number_type: Optional[CDDNumberType] = None) -> cdd.Polyhedron:
		M = _concat([
			_concat([self.be[:,None], -self.Ae], axis = 1),
			_concat([self.bu[:,None], -self.Au], axis = 1),
		], axis = 0)
		mat = cdd.Matrix(M, number_type = number_type or 'float')
		mat.lin_set = frozenset(range(self.Ae.shape[0]))
		mat.rep_type = cdd.RepType.INEQUALITY
		return cdd.Polyhedron(mat)
	
	def to_v(self, *, number_type: Optional[CDDNumberType] = None) -> 'VRepr':
		"""
			Convert to V-representation.
		"""
		mat = self.to_cdd_polyhedron(number_type = number_type).get_generators()
		return VRepr.from_cdd_matrix(mat, dtype = self.dtype)
	
	@classmethod
	def from_cdd_matrix(cls, mat: cdd.Matrix, *, dtype: Optional[Any] = None) -> 'HRepr':
		if dtype is None:
			dtype = np.float64
		
		Al = []
		bl = []
		
		for i in range(mat.row_size):
			bi, *nAi = mat[i]
			Al.append(nAi)
			bl.append(bi)
		A = -np.array(Al, dtype = dtype)
		b = np.array(bl, dtype = dtype)
		
		e = np.zeros(mat.row_size, dtype = np.bool_)
		e[list(mat.lin_set)] = True
		u = ~e
		
		return cls(A[u], b[u], A[e], b[e])

class VRepr:
	"""
		A polytope defined as the Minkowski sum of the convex hull of a set of points (Vc)
		and a cone (Vn and Vl); a.k.a. V-representation.
		> conv(Vc) + { Vn @ w | w in R^dim; w >= 0 } + { Vl @ w | w in R^dim }
	"""
	
	dim: int
	dtype: DType
	
	# Convex (Vc) and cone (Vn and Vl) components.
	# Shape: (*, dim)
	Vc: NDArray # convex
	Vn: NDArray # cone, [n]onnegative
	Vl: NDArray # cone, [l]inear
	
	def __init__(
		self,
		Vc: Optional[NDArray] = None,
		Vn: Optional[NDArray] = None,
		Vl: Optional[NDArray] = None,
	) -> None:
		V = _first_not_None(Vc, Vn, Vl)
		assert V is not None
		self.dim = V.shape[1]
		self.dtype = V.dtype
		
		if Vc is None:
			Vc = np.empty((0, self.dim), dtype = V.dtype)
		if Vn is None:
			Vn = np.empty((0, self.dim), dtype = V.dtype)
		if Vl is None:
			Vl = np.empty((0, self.dim), dtype = V.dtype)
		
		self.Vc = Vc
		self.Vn = Vn
		self.Vl = Vl
	
	def to_finite_basis(self) -> Tuple[NDArray, NDArray]:
		"""
			Consolidate cone part into nonnegative representation only:
			> conv(Vc) + { Vn @ w | w in R^dim; w >= 0 }
		"""
		Vn = self.Vn
		if len(self.Vl) > 0:
			Vn = _concat([Vn, self.Vl, -self.Vl], axis = 0)
		return self.Vc, Vn
	
	def to_cdd_polyhedron(self, *, number_type: Optional[CDDNumberType] = None) -> cdd.Polyhedron:
		M = _concat([self.Vl, self.Vc, self.Vn], axis = 0)
		M = _concat([np.zeros_like(M[:,:1]), M], axis = 1)
		M[len(self.Vl):len(self.Vl) + len(self.Vc), 0] = 1
		mat = cdd.Matrix(M, number_type = number_type or 'float')
		mat.lin_set = frozenset(range(len(self.Vl)))
		mat.rep_type = cdd.RepType.GENERATOR
		return cdd.Polyhedron(mat)
	
	def to_h(self, *, number_type: Optional[CDDNumberType] = None) -> 'HRepr':
		"""
			Convert to H-representation.
		"""
		mat = self.to_cdd_polyhedron(number_type = number_type).get_inequalities()
		return HRepr.from_cdd_matrix(mat, dtype = self.dtype)
	
	@classmethod
	def from_cdd_matrix(cls, mat: cdd.Matrix, *, dtype: Optional[Any] = None) -> 'VRepr':
		if dtype is None:
			dtype = np.float64
		
		Vcl: List[List[float]] = []
		Vnl: List[List[float]] = []
		Vll: List[List[float]] = []
		
		for i in range(mat.row_size):
			t, *row = mat[i]
			V = (Vcl if t > 0.5 else (Vll if i in mat.lin_set else Vnl))
			V.append(row)
		
		dim = mat.col_size - 1
		if Vcl:
			Vc = np.array(Vcl, dtype = dtype)
		else:
			Vc = np.empty((0, dim), dtype = dtype)
		if Vnl:
			Vn = np.array(Vnl, dtype = dtype)
		else:
			Vn = np.empty((0, dim), dtype = dtype)
		if Vll:
			Vl = np.array(Vll, dtype = dtype)
		else:
			Vl = np.empty((0, dim), dtype = dtype)
		
		return cls(Vc, Vn, Vl)

def _first_not_None(*mats: Optional[NDArray]) -> Optional[NDArray]:
	for m in mats:
		if m is not None:
			return m
	return None

def _concat(mats: List[NDArray], *, axis: int) -> NDArray:
	return np.concatenate(mats, axis = axis) # type: ignore
