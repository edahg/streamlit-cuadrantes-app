def load_data(file_path):
    import pandas as pd
    return pd.read_excel(file_path)

def filter_data(df, start_date, end_date, cambio_cuadrante):
    mask = (df['Año_Mes'] >= start_date) & (df['Año_Mes'] <= end_date) & (df['Cambio_cuadrante'] == cambio_cuadrante)
    return df.loc[mask]