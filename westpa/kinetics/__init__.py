'''
Kinetics analysis library
'''

import logging
log = logging.getLogger(__name__)


from rate_averaging import RateAverager

import _kinetics
from _kinetics import (accumulate_labeled_populations, calculate_labeled_fluxes, labeled_flux_to_rate, #@UnresolvedImport
                       calculate_labeled_fluxes_alllags, #@UnresolvedImport
                       nested_to_flat_matrix, nested_to_flat_vector, #@UnresolvedImport
                       flat_to_nested_matrix, flat_to_nested_vector, find_macrostate_transitions) #@UnresolvedImport

"""
Internally, "labeled" objects (bin populations labeled by history, rate matrix elements labeled
by history) are stored as nested arrays -- e.g. rates[initial_label, final_label, initial_bin, final_bin].
These are converted to the flat forms required for, say, eigenvalue calculations internally, and the 
results converted back. This is because these conversions are not expensive, and saves users of 
this code from having to know how the flattened indexing works (something I screwed up all too
easily during development) -- mcz
"""

"""
Bin populations are treated separately from labeled bin populations because trajectories 
initiating in a transition region do not contribute to the labeled bin populations. -- mcz
"""

import numpy
import scipy.linalg
import scipy.sparse.linalg


from west.data_manager import weight_dtype
from collections import namedtuple

def get_steady_state(rates):
    rates = rates.copy()
    
    # Convert to a transition probability matrix
    for i in xrange(rates.shape[0]):
        rowsum = rates[i].sum()
        if rowsum > 0:
            rates[i] = rates[i] / rowsum
        else:
            if rates[:,i].sum() != 0:
                # matrix not stable -- internal sink
                return None
            else:
                rates[i] = 0
                    
    try:
        vals, vecs = scipy.linalg.eig(rates.T)
    except Exception as e:
        return None
    
    vals = numpy.abs(vals)
    asort = numpy.argsort(vals)
    vec = vecs[:,asort[-1]]    
    ss = numpy.abs(vec)
    
    ss /= ss.sum()
    return ss

def get_macrostate_rates(labeled_rates, labeled_pops):
    '''Using a labeled rate matrix and labeled bin populations, calculate the steady state
    probability distribution and consequent state-to-state rates.
    
    Returns ``(ss, macro_rates)``, where ``ss`` is the steady-state probability distribution
    and ``macro_rates`` is the state-to-state rate matrix.'''
    
    nstates, nbins = labeled_pops.shape
        
    rates = nested_to_flat_matrix(labeled_rates)
        
    # Find steady-state solution
    ss = get_steady_state(rates)
    if ss is None:
        log.warning('no well-defined steady state; using average populations')
        ss = nested_to_flat_vector(labeled_pops)
    macro_rates = numpy.zeros((nstates,nstates), weight_dtype)
    
    # Sum over bins contributing to each state
    for istate in xrange(nstates):
        for jstate in xrange(nstates):
            for ibin in xrange(nbins):
                for jbin in xrange(nbins):
                    #sspop = ss[istate*nstates+ibin]
                    #rateelem = rates[istate*nbins+ibin,jstate*nbins+jbin]
                    sspop = ss[ibin*nstates+istate]
                    rateelem = rates[ibin*nstates+istate,jbin*nstates+jstate]
                    #print('state {}->{} bin {}->{} pop {} rate {}'.format(istate,jstate,ibin,jbin,sspop,rateelem))
                    macro_rates[istate,jstate] += sspop*rateelem
    
    # Normalize by total population in each trajectory ensemble
    for istate in xrange(nstates):
        traj_ens_pop = labeled_pops[istate].sum()
        macro_rates[istate] /= traj_ens_pop

    return flat_to_nested_vector(nstates, nbins, ss), macro_rates

_rate_result = namedtuple('_rate_result', ('labeled_bin_pops','labeled_bin_fluxes'))

def estimate_rates(nbins, state_labels, weights, parent_ids, bin_assignments, label_assignments, state_map,
                   all_lags=False):
    '''Estimate rates over multiple iterations.
    Returns unlabeled and labeled bin populations, labeled flux matrix, and
    (the instantaneous estimate of) the rate matrix.'''
    
    assert len(weights) == len(parent_ids) == len(bin_assignments) == len(label_assignments)
    
    niters = len(weights)
    nstates = len(state_labels)
        
    # Estimate microstate and trajectory populations over entire window
    labeled_bin_pops = numpy.zeros((nstates,nbins), weight_dtype)
    
    for iiter in xrange(niters):
        accumulate_labeled_populations(weights[iiter], bin_assignments[iiter], label_assignments[iiter], labeled_bin_pops)
    
    labeled_bin_pops /= niters 
        
    # Loop over all possible windows to accumulate flux matrix
    # flux matrix is [initial_label][final_label][initial_bin][final_bin]
    fluxes = numpy.zeros((nstates, nstates, nbins, nbins), weight_dtype)
    if all_lags:
        twindow = calculate_labeled_fluxes_alllags(nstates, weights, parent_ids, bin_assignments, label_assignments, fluxes)
    else:
        twindow = calculate_labeled_fluxes(nstates, weights, parent_ids, bin_assignments, label_assignments, fluxes)
    fluxes /= twindow
        
    return _rate_result(labeled_bin_pops, fluxes)

