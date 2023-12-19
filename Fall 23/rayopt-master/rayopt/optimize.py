#
#   rayopt - raytracing for optical imaging systems
#   Copyright (C) 2012 Robert Jordens <robert@joerdens.org>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


from fastcache import clru_cache
import numpy as np
from scipy.optimize import minimize


class Variable:
    def __init__(self, system, bounds=(-np.inf, np.inf),
                 scale=None, init=None):
        self.system = system
        if scale is None:
            range = bounds[1] - bounds[0]
            assert np.isfinite(range)
            scale = range
        self.scale = scale
        self.bounds = bounds
        if init is None:
            init = self.get()
        self.init = init

    def get(self):
        raise NotImplementedError

    def set(self, value):
        raise NotImplementedError


class PathVariable(Variable):
    def __init__(self, system, path, *args, **kwargs):
        self.path = path
        super().__init__(system, *args, **kwargs)

    def get(self):
        return self.system.get_path(self.path)

    def set(self, value):
        self.system.set_path(self.path, value)


class Operand:
    def __init__(self, system, weight=None, offset=0,
                 min=None, max=None):
        self.system = system
        self.weight = weight
        self.offset = offset
        self.min = min
        self.max = max

    def get(self):
        raise NotImplementedError

    def get_objective(self):
        if self.weight:
            yield lambda v: self.weight*(v - self.offset)

    def get_equality(self):
        if self.min is not None and self.min == self.max:
            yield lambda v: v - self.offset

    def get_inequality(self):
        if self.min is not None:
            yield lambda v: v - self.offset - self.min
        if self.max is not None:
            yield lambda v: self.max - (v - self.offset)


class FuncOp(Operand):
    def __init__(self, system, func, *args, **kwargs):
        super().__init__(system, *args, **kwargs)
        self.func = func

    def get(self):
        return np.atleast_1d(self.func(self.system)).ravel()


def optimize(variables, operands, callback=None, tol=1e-4, options={},
             trace=False, **kwargs):
    assert variables
    assert operands
    s = np.array([v.scale for v in variables])
    x0 = np.array([v.get() for v in variables])/s
    x1 = np.array([v.init for v in variables])/s
    bounds = np.array([v.bounds for v in variables])/s[:, None]

    ob, eq, ineq = [], [], []
    for i, op in enumerate(operands):
        for obi in op.get_objective():
            ob.append((i, obi))
        for eqi in op.get_equality():
            eq.append((i, eqi))
        for ineqi in op.get_inequality():
            ineq.append((i, ineqi))
    assert ob

    def up(x):
        for xi, vi in zip(x*s, variables):
            vi.set(xi)

    @clru_cache(maxsize=len(variables) + 1)
    def ex(*x):
        up(x)
        return [op.get() for op in operands]

    def fun(x):
        v = ex(*x)
        o = np.concatenate([obi(v[i]) for i, obi in ob])
        return np.square(o).sum()

    def feq(x):
        v = ex(*x)
        return np.concatenate([eqi(v[i]) for i, eqi in eq])

    def fineq(x):
        v = ex(*x)
        return np.concatenate([ineqi(v[i]) for i, ineqi in ineq])

    cons = []
    if eq:
        cons.append({"type": "eq", "fun": feq})
    if ineq:
        cons.append({"type": "ineq", "fun": fineq})

    xi, vi, fi = [], [], []

    def cb(x):
        if trace:
            v = ex(*x)
            xi.append(x*s)
            vi.append(v)
            fi.append([obi(v[i]) for i, obi in ob])
        if callback:
            return callback(x)

    opts = dict(maxiter=100, eps=1e-5)
    opts.update(options)
    r = minimize(fun, x1, bounds=bounds, constraints=cons, callback=cb,
                 tol=tol, options=opts, **kwargs)
    r.accept = lambda: up(r.x)
    r.reject = lambda: up(x0)
    r.trace_x = np.array(xi)
    r.trace_v = vi
    r.trace_f = [(i, np.array([fj[j] for fj in fi]))
                 for j, (i, obi) in enumerate(ob)]
    return r
