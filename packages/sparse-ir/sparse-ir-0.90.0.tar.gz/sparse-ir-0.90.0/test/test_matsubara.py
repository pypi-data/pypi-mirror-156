# Copyright (C) 2020-2022 Markus Wallerberger, Hiroshi Shinaoka, and others
# SPDX-License-Identifier: MIT
import numpy as np
import pytest
import importlib

from sparse_ir.basis import FiniteTempBasis
from sparse_ir.spr import SparsePoleRepresentation

eps = None
if importlib.util.find_spec("xprec") is not None:
    eps = 1.0e-15

all_basis_sets = [(stat, lambda_)
                  for stat in 'FB' for lambda_ in [1E+1, 1E+4]]

"""
A pole at omega=pole. Compare analytic results of G(iwn) and numerical
results computed by using unl.
"""
@pytest.mark.parametrize("stat, lambda_", all_basis_sets)
def test_single_pole(sve_logistic, stat, lambda_):
    wmax = 1.0
    pole = 0.1 * wmax
    beta = lambda_ / wmax
    sve_result = sve_logistic[lambda_]
    basis = FiniteTempBasis(stat, beta, wmax, eps, sve_result=sve_result)

    if stat == 'F':
        stat_shift = 1
    else:
        stat_shift = 0
    spr = SparsePoleRepresentation(basis, np.asarray([pole]))
    gl = spr.to_IR(np.asarray([1.0]))

    func_G = lambda n: 1/(1J * (2*n+stat_shift)*np.pi/beta - pole)

    # Compute G(iwn) using unl
    matsu_test = np.array([-1, 0, 1, 1E+2, 1E+4, 1E+6, 1E+8, 1E+10, 1E+12],
                          dtype=np.int64)
    prj_w = basis.uhat(2*matsu_test+stat_shift).T
    Giwn_t = prj_w @ gl

    # Compute G(iwn) from analytic expression
    Giwn_ref = func_G(matsu_test)

    magnitude = np.abs(Giwn_ref).max()
    diff = np.abs(Giwn_t - Giwn_ref)

    tol = max(10 * basis.s[-1]/basis.s[0], 1e-10)

    # Absolute error
    assert (diff/magnitude).max() < tol

    # Relative error
    #print("relative: error ", np.abs(diff/Giwn_ref))
    assert np.amax(np.abs(diff/Giwn_ref)) < tol
