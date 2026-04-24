# utils/horarios.py
# CYBER TRADE WIN — Single Source of Truth para horários
# WIN (WINFUT / Mini Ibovespa) — sessão B3

from datetime import datetime, time


# ─── Horários oficiais da sessão WIN ────────────────────────────────────────
WIN_ABERTURA = time(9, 0) # pré-abertura — não operar
WIN_INICIO_OPERACAO = time(9, 15) # início seguro de operação
WIN_ALMOCO_INICIO = time(12, 0) # início do horário de almoço
WIN_ALMOCO_FIM = time(13, 30) # fim do horário de almoço
WIN_CUTOFF_OPERACAO = time(17, 15) # CUTOFF — parar de abrir novas posições
WIN_FECHAMENTO_SESSAO = time(17, 55) # encerramento da sessão B3

# Margem de segurança para fechar posições antes do cutoff (minutos)
WIN_MARGEM_FECHAMENTO_MIN = 5


def cutoff_atingido() -> bool:
    """Retorna True se o horário atual passou do cutoff operacional do WIN."""
    agora = datetime.now()
    cutoff = agora.replace(
        hour=WIN_CUTOFF_OPERACAO.hour,
        minute=WIN_CUTOFF_OPERACAO.minute,
        second=0,
        microsecond=0
    )
    return agora >= cutoff


def horario_proibido() -> tuple[bool, str]:
    """
    Retorna (True, motivo) se o horário atual é proibido para operar.
    Retorna (False, '') se é horário válido.
    """
    agora = datetime.now().time()

    # Pré-abertura: não operar
    if agora < WIN_INICIO_OPERACAO:
        return True, f"Pre-abertura ({agora.strftime('%H:%M')} < {WIN_INICIO_OPERACAO.strftime('%H:%M')})"

    # Horário de almoço: volume baixo, fakes frequentes
    if WIN_ALMOCO_INICIO <= agora < WIN_ALMOCO_FIM:
        return True, f"Almoco ({WIN_ALMOCO_INICIO.strftime('%H:%M')}-{WIN_ALMOCO_FIM.strftime('%H:%M')})"

    # Próximo do cutoff: apenas fechar posições abertas
    if agora >= WIN_CUTOFF_OPERACAO:
        return True, f"Pos-cutoff ({agora.strftime('%H:%M')} >= {WIN_CUTOFF_OPERACAO.strftime('%H:%M')})"

    return False, ""


def minutos_para_cutoff() -> int:
    """Retorna quantos minutos faltam para o cutoff operacional."""
    agora = datetime.now()
    cutoff = agora.replace(
        hour=WIN_CUTOFF_OPERACAO.hour,
        minute=WIN_CUTOFF_OPERACAO.minute,
        second=0,
        microsecond=0
    )
    diff = (cutoff - agora).total_seconds()
    return max(0, int(diff / 60))


def em_horario_valido() -> bool:
    """Retorna True se está em horário válido para operar."""
    proibido, _ = horario_proibido()
    return not proibido


def get_status_horario() -> dict:
    """Retorna dict com status completo do horário para os agentes."""
    proibido, motivo = horario_proibido()
    mins_cutoff = minutos_para_cutoff()
    agora = datetime.now()

    return {
        "horario_atual": agora.strftime("%H:%M:%S"),
        "horario_valido": not proibido,
        "motivo_bloqueio": motivo if proibido else "",
        "minutos_para_cutoff": mins_cutoff,
        "alerta_pre_cutoff": mins_cutoff <= 15, # alerta 15 min antes
        "cutoff_atingido": cutoff_atingido(),
        "sessao_ativa": WIN_ABERTURA <= agora.time() <= WIN_FECHAMENTO_SESSAO,
    }
