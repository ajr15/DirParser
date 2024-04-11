try: 
    import openbabel as ob
    from .openbabel import atomic_numer_to_symbol, atomic_symbol_to_number
except ImportError:
    try:
        pass
    except ImportError:
        pass