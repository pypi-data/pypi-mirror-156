"""
Load a seed data frame and extract information needed to set up the
ancestral sequence reconstruction calculation.
"""

import topiary

import numpy as np
import pandas as pd

import re, itertools
from string import ascii_lowercase, digits

def _get_string_variants(some_string,spacers):
    """
    Get regular expressions describing strings with variable spacers. For
    example LY96, LY-96, LY 96, LY_96. This function looks for elements in
    spacers or transitions between letters and numbers and builds regular
    expressions to match those patterns. It makes all letters lowercase
    and thus expects to be used in a regular expression ignoring case.

    Examples (for spacers = [" ","-","_","."]):
        "LY96" -> "ly[\ \-_\.]*96"
        "MD-2" -> "md[\ \-_\.]*2"
        "myeloid factor 2" -> "myeloid[\ \-_\.]*factor[\ \-_\.]*2"
        "CDR2L" -> "cdr[\ \-_\.]*2[\ \-_\.]*L"

    Parameters
    ----------
    some_string : string to process
        spacers: list of characters to recognize as spacers

    Return
    ------
        regular expression as a string
    """

    # Regular expression describing spacers
    spacer_re = "".join([re.escape(s) for s in spacers])
    spacer_re = f"[{spacer_re}]*"

    # Make lowercase and strip leading/trailing white space
    lower = some_string.lower().strip()

    # Get digit, letter, and spacer characters
    is_digit = np.zeros(len(lower),dtype=bool)
    is_letter = np.zeros(len(lower),dtype=bool)
    is_spacer = np.zeros(len(lower),dtype=bool)
    for i, s in enumerate(lower):
        if s in digits:
            is_digit[i] = True
        elif s in ascii_lowercase:
            is_letter[i] = True
        elif s in spacers:
            is_spacer[i] = True
        else:
            pass

    # Go through sequence and build pattern character by character
    pattern = []
    for i in range(len(lower)-1):

        # If we hit a spacer, put in non-greedy match
        if is_spacer[i]:
            pattern.append(spacer_re)
            continue

        # Append the letter/digit we saw
        pattern.append(lower[i])

        # Digit followed by letter
        if is_digit[i] and is_letter[i+1]:
            pattern.append(spacer_re)

        # Letter followed by digit
        if is_letter[i] and is_digit[i+1]:
            pattern.append(spacer_re)

    # Last letter
    pattern.append(lower[-1])

    return "".join(pattern)


def _get_alias_regex(list_of_names,spacers=[" ","-","_","."]):
    """
    Produce a regular expression that matches all patterns in list of names,
    expanding all spacers characters to look for all possiblities at that
    site. For example, names might be ["LY96", "MD2", "ESOP1"]. These will be
    put into _get_string_variants, yielding a final regular expression:
        "ly[\ \-_.]*96|md[\ \-_.]*2|esop[\ \-_.]*1"

    Parameters
    ----------
        list_of_names: list of strings from which to build the regex.
        spacers: list of characters to recognize as spacers

    Return
    ------
        compiled regular expression instance
    """

    # Make unique set of names
    list_of_names = list(set(list_of_names))



    # Make regular expression for each name
    all_names = []
    for n in list_of_names:
        all_names.append(_get_string_variants(n,spacers))

    # Unique set of regex
    all_names = list(set(all_names))

    # sort for testing purposes so regex has predictable order
    all_names.sort()

    return re.compile("|".join(all_names),flags=re.IGNORECASE)


def load_seed_dataframe(df):
    """
    Load a seed data frame and extract information needed to set up the
    ancestral sequence reconstruction calculation.

    Parameters
    ----------
    df: pandas.DataFrame or str
        seed dataframe containing seed sequences to launch the analysis. df can
        be a pandas dataframe or a string pointing to a spreadsheet file.

    Returns
    -------
    topiary_dataframe : pandas.DataFrame
        new topiary dataframe build from the seed dataframe
    phylo_context : str
        string descriptor of the phylogenetic context on opentreeoflife.org
        (i.e. "Animals" or "All life")
    key_species : list
        list if key species to keep during the analysis
    paralog_patterns : list
        list of compiled regular expressions (extracted from aliases) to use to
        try to match paralogs.

    Notes
    -----

    The seed dataframe is expected to have at least four columns:

    + `species`: species names for seed sequences in binomial format (i.e.
      Homo sapiens or Mus musculus)
    + `name`: name of each sequence (i.e. LY96)
    + `aliases`: other names for this sequence found in different
      databases/species, separated by ; (i.e. LY96;MD2;ESOP1)
    + `sequence`: amino acid sequences for these proteins.

    Other columns in the dataframe are kept but not used by topiary.
    """

    # -----------------------------------------------------------------------
    # Load dataframe and check it's sanity

    if type(df) is not type(pd.DataFrame()):

        if type(df) is str:
            extension = df.split(".")[-1].strip().lower()
            if extension in ["xls","xlsx"]:
                df = pd.read_excel(df)
            elif extension == "csv":
                df = pd.read_csv(df,sep=",")
            elif extension == "tsv":
                df = pd.read_csv(df,sep="\t")
            else:
                df = pd.read_csv(df,sep=None,engine="python")
        else:
            err = f"Could not figure out how to read df '{df}'\n\n"
            raise ValueError(err)

    required_columns = ["species","name","aliases","sequence"]
    for c in required_columns:

        try:
            df[c]
        except KeyError:
            err = f"\nDataframe must have a {c} column. Required columns are:\n"
            for r in required_columns:
                err += f"    {r}\n"
            err += "\n"
            raise ValueError(err)

    # -----------------------------------------------------------------------
    # Get key_species and phylogenetic context

    key_species = list(np.unique(df.loc[:,"species"]))
    key_species.sort() # sort alphabetically

    phylo_context = topiary.opentree.get_phylo_context(key_species)

    # -----------------------------------------------------------------------
    # Construct paralog_patterns

    # Build a paralog_patterns dictionary
    alias_dict = {}
    for idx in df.index:

        # Construct list of all aliases given by the user for a given name
        key = str(df.loc[idx,"name"])
        values = [v.strip() for v in df.loc[idx,"aliases"].split(";")]

        try:
            alias_dict[key].extend(values)
        except KeyError:
            alias_dict[key] = values[:]

    paralog_patterns = {}
    for a in alias_dict:

        # Put name itself in as an alias
        alias_dict[a].append(a)

        # Get regular expression representations of these patterns
        paralog_patterns[a] = _get_alias_regex(alias_dict[a])

    # Load newly created paralog patterns into aliases column
    new_aliases = []
    for idx in df.index:

        name = df.loc[idx,"name"]
        new_aliases.append(paralog_patterns[name].pattern)

    df.loc[:,"aliases"] = new_aliases


    # -----------------------------------------------------------------------
    # Convert dataframe into a topiary dataframe

    # add always keep column to this dataframe
    df["always_keep"] = True

    # Drop on uid column to avoid warning when topiary creates in arg_processor
    try:
        df["uid"]
    except KeyError:
        df["uid"] = topiary._private.generate_uid(len(df["always_keep"]))

    df = topiary.check.check_topiary_dataframe(df)

    return df, phylo_context, key_species, paralog_patterns
