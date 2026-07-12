# utils/calculos.py
# Funciones de conversión y cálculo para el sistema de café

def cajuelas_a_texto(cajuelas: float) -> str:
    """
    Convierte un número de cajuelas a texto legible.
    Ejemplo: 4.25 → '4 cajuelas y 1 cuarto'
             5.50 → '5 cajuelas y media'
             6.75 → '6 cajuelas y 3 cuartos'
             7.00 → '7 cajuelas'
    """
    # Separar la parte entera de la decimal
    enteras = int(cajuelas)
    fraccion = round(cajuelas - enteras, 2)

    # Determinar el texto de la fracción
    if fraccion == 0:
        fraccion_texto = ""
    elif fraccion == 0.25:
        fraccion_texto = " y 1 cuarto"
    elif fraccion == 0.50:
        fraccion_texto = " y media"
    elif fraccion == 0.75:
        fraccion_texto = " y 3 cuartos"
    else:
        # Si no es múltiplo exacto de 0.25, mostrar el número
        fraccion_texto = f" y {fraccion}"

    # Singular o plural
    unidad = "cajuela" if enteras == 1 and fraccion == 0 else "cajuelas"

    return f"{enteras} {unidad}{fraccion_texto}"


def cajuelas_a_fanegas(cajuelas: float) -> str:
    """
    Convierte cajuelas a fanegas con texto legible.
    Ejemplo: 25.5 cajuelas → '1 fanega y 5 cajuelas y media'
    """
    # 1 fanega = 20 cajuelas
    fanegas_enteras = int(cajuelas // 20)
    cajuelas_restantes = cajuelas % 20

    if fanegas_enteras == 0:
        return cajuelas_a_texto(cajuelas_restantes)

    fanega_unidad = "fanega" if fanegas_enteras == 1 else "fanegas"

    if cajuelas_restantes == 0:
        return f"{fanegas_enteras} {fanega_unidad}"

    return f"{fanegas_enteras} {fanega_unidad} y {cajuelas_a_texto(cajuelas_restantes)}"


def cajuelas_a_numero(cajuelas: float) -> float:
    """
    Redondea cajuelas al cuarto más cercano (0.25).
    Ejemplo: 4.3 → 4.25, 5.6 → 5.50
    """
    return round(cajuelas * 4) / 4