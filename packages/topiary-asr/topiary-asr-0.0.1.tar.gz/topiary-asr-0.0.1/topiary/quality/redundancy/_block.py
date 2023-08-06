"""
Functions for lowering redundnacy based on clusters of similar sequence
identity.
"""

from Bio import pairwise2

import numpy as np

def _compare_seqs(A_seq,B_seq,A_qual,B_qual,cutoff,discard_key=False):
    """
    Compare sequence A and B based on alignment. If the sequences are
    similar within cutoff, compare A_stats and B_stats and take the sequence
    with the lower score. Scores have left-right priority.  Will select
    sequence with the first element with a lower score. If sequences are
    similar within cutoff and have equal scores, choose A.

    Parameters
    ----------
        A_seq: sequence A
        B_seq: sequence B
        A_qual: quality scores for A
        B_qual: quality scores for B
        cutoff: cutoff for sequence comparison (~seq identity. between 0 and 1)
        discard_key: whether or not to discard key species, regardless of their
                     qualities.

    Return
    ------
        bool, bool

        True, True: keep both
        True, False: keep A
        False, True: keep B
    """

    # Get a normalized score: matches/len(shortest)
    score = pairwise2.align.localxx(A_seq,B_seq,score_only=True)
    norm = score/np.min((len(A_seq),len(B_seq)))

    # If sequence similarity is less than the cutoff, keep both
    if norm <= cutoff:
        return True, True

    # If sequence similarity is greater than the cutoff, select one.
    else:

        # If both always keep, return that we keep both
        if A_qual[0] == 0 and B_qual[0] == 0:
            return True, True

        # If we are not discarding key sequences and both sequences are
        # from key species, automatically keep both.
        if not discard_key:
            if A_qual[1] == 0 and B_qual[1] == 0:
                return True, True

        # Compare two vectors. Identify first element that differs.

        # Return
        #   True, False if A is smaller
        #   False, True if B is smaller
        #   True, False if equal

        comp = np.zeros(A_qual.shape[0],dtype=np.int8)
        comp[B_qual > A_qual] = 1
        comp[B_qual < A_qual] = -1
        diffs = np.nonzero(comp)[0]

        # No difference, keep A arbitrarily
        if diffs.shape[0] == 0:
            return True, False

        # B > A at first difference, keep A
        elif comp[diffs[0]] > 0:
            return True, False

        # B < A at first difference, keep B
        else:
            return False, True

def _check_block_redundancy(args):
    """
    Check for redundancy within a block of the sequence by sequence matrix.
    Updates keep_array in a thread-safe manner. Should be called by
    _reduce_redundancy_thread_manager.


    Parameters
    ----------
        args: iterable of arguments. Expanded to:

        i_block: tuple holding indexes over which to iterate in i
        j_block: tuple holding indexes over which to interate in j
        sequence_array: array holding sequences to compare.
        quality_array: array holding vectors of quality scores, one vector for
                       each sequence
        keep_array: array holding whether or not to keep each sequence. boolean.
                    This array is updated and is the primary output of this
                    function.
        cutoff: float cutoff between 0 and 1 indicating the fractional similarity
                between two sequences above which they are considered redundant.
        discard_key: if discard_key is False, a redundant sequence will be tossed
                     even if it is from a key species
        lock: multiprocessing.Lock instance used to control access to keep_array

    Return
    ------
        None. Updates keep_array in place.
    """

    i_block = args[0]
    j_block = args[1]
    sequence_array = args[2]
    quality_array = args[3]
    keep_array = args[4]
    cutoff = args[5]
    discard_key = args[6]
    lock = args[7]

    # Lock keep_array and make a local copy
    lock.acquire()
    try:
        local_keep = keep_array.copy()
    finally:
        lock.release()

    # Loop over block in i
    for i in range(i_block[0],i_block[1]):

        # Skip if we already know we're not keeping i
        if not local_keep[i]:
            continue

        # Loop over block in j
        for j in range(j_block[0],j_block[1]):

            # Skip if we're below or at diagonal
            if j <= i:
                continue

            # Skip if we already know we're not keeping j
            if not local_keep[j]:
                continue

            # Make comparison
            i_keep, j_keep = _compare_seqs(sequence_array[i],
                                           sequence_array[j],
                                           quality_array[i],
                                           quality_array[j],
                                           cutoff,
                                           discard_key=discard_key)

            # Record results
            local_keep[i] = i_keep
            local_keep[j] = j_keep

            # Not keeping i, we don't need to keep going
            if not i_keep:
                break

    # Lock keep_array and update with what we learned in local_keep. This is
    # an "and" operation. Only keep if keep_array AND local_keep are still True.
    lock.acquire()
    try:
        keep_array[:] = np.logical_and(keep_array,local_keep)
    finally:
        lock.release()
