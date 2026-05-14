"""Python port of the MERFISH codebook generator from Boström, Zapała & Adameyko,
Science Advances 11(18), eadr4026 (2025); DOI 10.1126/sciadv.adr4026; PMID 40315316;
PMC12047430.
"""

from .hd import evaluate_hd_matrix, validate_min_hd
from .johnson import johnson_bound

__all__ = [
    "evaluate_hd_matrix",
    "validate_min_hd",
    "johnson_bound",
]

# The pipeline / Start / CodebookResult symbols are added once those modules exist.
try:
    from .pipeline import CodebookResult, Start, generate_codebook  # noqa: F401
    __all__ += ["CodebookResult", "Start", "generate_codebook"]
except ImportError:
    pass

__version__ = "0.1.0"
