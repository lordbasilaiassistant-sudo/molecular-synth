"""
makerlib - the Maker Catalog: an ever-extending, queryable library of what one
synthesizer-system can make, with an honest feasibility verdict per item.

    from makerlib import check, list_catalog
    print(check("cookie"))

CLI:  python -m makerlib check "glass of cold water"
      python -m makerlib list [--feasibility ready]

Extend it by adding an item to catalog/items.json (the cookie principle: decompose into
components -> molecules -> atoms; DNA/proteins where biological), then check it.
"""
from .checker import check, list_catalog, load_catalog, find   # noqa: F401
from .order import order, interpret, fulfill                    # noqa: F401

__version__ = "0.1.0"
