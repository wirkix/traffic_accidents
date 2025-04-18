from charset_normalizer import from_path

def detect_encoding(file_path):
    result = from_path(file_path)
    best_guess = result.best()
    if best_guess is None:
        raise Exception(f"No se pudo detectar el encoding de {file_path}.")
    return best_guess.encoding

def read_csv_utf8_cleaned(file_path):
    """
    Detecta el encoding, lee el CSV, limpia caracteres invisibles y devuelve un DataFrame.
    """
    import pandas as pd

    encoding = detect_encoding(file_path)

    with open(file_path, "r", encoding=encoding, errors="replace") as f:
        content = f.read()

    cleaned = content.replace('\xa0', ' ').replace('\ufeff', '')
    
    from io import StringIO
    return pd.read_csv(StringIO(cleaned), low_memory=False)
