from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta
import calendar

# =============================================================================
# SEZIONE 1: CONVERSIONI BASE (Stringa <-> Oggetto)
# =============================================================================

def from_date_to_string(d: datetime) -> str:
    """Converte oggetto datetime in stringa 'gg-mm-YYYY'"""
    return d.strftime("%d-%m-%Y")

def from_string_to_date(d_str: str) -> datetime:
    """Converte stringa 'gg-mm-YYYY' in oggetto datetime"""
    try:
        return datetime.strptime(d_str, "%d-%m-%Y")
    except (ValueError, TypeError):
        return None

def from_time_to_string(t: time) -> str:
    """Converte oggetto time in stringa 'HH:MM'"""
    return t.strftime("%H:%M")

def from_string_to_time(t_str: str) -> time:
    """Converte stringa 'HH:MM' in oggetto time"""
    try:
        return datetime.strptime(t_str, "%H:%M").time()
    except (ValueError, TypeError):
        return None

def from_month_to_string(m: datetime) -> str:
    """Converte oggetto datetime in stringa 'MM-YYYY'"""
    return m.strftime("%m-%Y")

def from_string_to_month(m_str: str) -> datetime:
    """Converte stringa 'MM-YYYY' in oggetto datetime"""
    try:
        return datetime.strptime(m_str, "%m-%Y")
    except (ValueError, TypeError):
        return None
    
# =============================================================================
# SEZIONE 2: LISTE E RANGE DI DATE
# =============================================================================

def get_past_dates(days: int, exclude_today: bool = False) -> list[str]:
    """
    Restituisce una lista di date (stringhe) passate.
    :param days: numero di giorni da recuperare
    :param exclude_today: se True, parte da ieri
    """
    today = datetime.today()
    start = 1 if exclude_today else 0
    return [
        (today - timedelta(days=i)).strftime("%d-%m-%Y")
        for i in range(start, start + days)
    ]

def giorni_della_settimana(data: datetime = datetime.today()) -> list[str]:
    """Restituisce la lista dei 7 giorni (stringhe) della settimana della data fornita"""
    inizio_settimana = data - timedelta(days=data.weekday()) # Lunedì
    return [
        (inizio_settimana + timedelta(days=i)).strftime("%d-%m-%Y")
        for i in range(7)
    ]

def giorni_del_mese(data: datetime = datetime.today()) -> list[str]:
    """Restituisce la lista di tutti i giorni (stringhe) del mese della data fornita"""
    num_giorni = calendar.monthrange(data.year, data.month)[1]
    inizio_mese = data.replace(day=1)
    return [
        (inizio_mese + timedelta(days=i)).strftime("%d-%m-%Y")
        for i in range(num_giorni)
    ]

def primo_e_ultimo_giorno_del_mese(data: datetime = datetime.today()) -> tuple[str, str]:
    """Restituisce una tupla (primo_giorno, ultimo_giorno) come stringhe"""
    giorni = giorni_del_mese(data)
    return giorni[0], giorni[-1]

# =============================================================================
# SEZIONE 3: OPERAZIONI MATEMATICHE E LOGICA
# =============================================================================

def somma_giorni(data_str: str, giorni: int) -> str:
    """Aggiunge n giorni a una data stringa"""
    d = from_string_to_date(data_str)
    if d:
        return from_date_to_string(d + timedelta(days=giorni))
    return data_str

def somma_mesi(data_str: str, mesi: int) -> str:
    """Aggiunge n mesi a una data stringa (richiede dateutil)"""
    d = from_string_to_date(data_str)
    if d:
        nuovo = d + relativedelta(months=mesi)
        return from_date_to_string(nuovo)
    return data_str

def somma_ore_minuti(orario_str: str, ore: int = 0, minuti: int = 0) -> str:
    """Aggiunge ore e minuti a un orario stringa HH:MM"""
    t_obj = datetime.strptime(orario_str, "%H:%M") # Uso datetime fittizio
    nuovo = t_obj + timedelta(hours=ore, minutes=minuti)
    return nuovo.strftime("%H:%M")

def calculate_end_time(start_time_str: str, duration_minutes: int) -> str:
    """
    Calcola l'orario di fine.
    Gestisce automaticamente il cambio di giornata (es. 23:00 + 120min -> 01:00).
    """
    try:
        # Trucco: Creiamo un datetime fittizio con la data di oggi e l'ora data
        dt_start = datetime.strptime(start_time_str, "%H:%M")
        dt_end = dt_start + timedelta(minutes=int(duration_minutes))
        return dt_end.strftime("%H:%M")
    except (ValueError, TypeError):
        return None

def overlap(t1_str: str, durata_1: int, t2_str: str, durata_2: int) -> bool:
    """Verifica se due intervalli temporali si sovrappongono"""
    def to_minutes(hhmm: str) -> int:
        try:
            h, m = map(int, hhmm.split(":"))
            return h * 60 + m
        except: return 0
    
    start1 = to_minutes(t1_str)
    end1 = start1 + int(durata_1)
    
    start2 = to_minutes(t2_str)
    end2 = start2 + int(durata_2)
    
    # Logica di sovrapposizione standard
    return max(start1, start2) < min(end1, end2)

# =============================================================================
# SEZIONE 4: ORDINAMENTO
# =============================================================================

def ordina_date(lista_date: list[str], crescente: bool = True) -> list[str]:
    """Ordina lista di date formato 'gg-mm-YYYY'"""
    return sorted(
        lista_date,
        key=lambda d: datetime.strptime(d, "%d-%m-%Y"),
        reverse=not crescente
    )

def ordina_mesi(lista_mesi: list[str], crescente: bool = True) -> list[str]:
    """Ordina lista di mesi formato 'mm-YYYY'"""
    return sorted(
        lista_mesi,
        key=lambda d: datetime.strptime(d, "%m-%Y"),
        reverse=not crescente
    )

def ordina_ore_minuti(lista_orari: list[str], crescente: bool = True) -> list[str]:
    """Ordina lista di orari formato 'HH:MM'"""
    return sorted(
        lista_orari,
        key=lambda t: datetime.strptime(t, "%H:%M"),
        reverse=not crescente
    )

# =============================================================================
# SEZIONE 5: UTILITY VARIE E FORMATTAZIONE
# =============================================================================

def giorno_della_settimana_it(data_str: str) -> str:
    """Restituisce il nome del giorno in italiano (es. 'Lunedì')"""
    data = from_string_to_date(data_str)
    if not data: return ""
    giorni = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    return giorni[data.weekday()]

def mese_it_month(month_str: str) -> str:
    """Restituisce il nome del mese in italiano (es. 'Gennaio')"""
    data = from_string_to_month(month_str)
    if not data:
        return ""

    mesi = [
        "Gennaio", "Febbraio", "Marzo", "Aprile",
        "Maggio", "Giugno", "Luglio", "Agosto",
        "Settembre", "Ottobre", "Novembre", "Dicembre"
    ]
    return mesi[data.month - 1]

def mese_it_date(date_str: str) -> str:
    """Restituisce il nome del mese in italiano (es. 'Gennaio')"""
    data = from_string_to_date(date_str)
    if not data:
        return ""

    mesi = [
        "Gennaio", "Febbraio", "Marzo", "Aprile",
        "Maggio", "Giugno", "Luglio", "Agosto",
        "Settembre", "Ottobre", "Novembre", "Dicembre"
    ]

    return mesi[data.month - 1]

def da_ddmmyyyy_a_yyyymmdd(data_str: str) -> str:
    """Converte '10-05-2025' -> '2025-05-10' (Utile per input HTML date)"""
    d = from_string_to_date(data_str)
    return d.strftime("%Y-%m-%d") if d else ""

def da_yyyymmdd_a_ddmmyyyy(data_str: str) -> str:
    """Converte '2025-05-10' -> '10-05-2025' (Da input HTML a formato interno)"""
    try:
        d = datetime.strptime(data_str, "%Y-%m-%d")
        return d.strftime("%d-%m-%Y")
    except:
        return ""
