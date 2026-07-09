from dataclasses import dataclass
import logging

import fitz

logger = logging.getLogger(__name__)


@dataclass
class Campo:
    ancora: str
    tipo: str
    valor: list[str]


class AnchorPdfFiller:
    ORDEM_ANCORAS = [
        "Depositário Central, Bolsas ou Entidades de Balcão Organizado?",
        "Entidade constituída em outro país ou sob leis estrangeiras?",
        "Capital e Cotistas / Acionistas",
        "Entidade possui sócio(s) americano com 25% ou mais",
        "Ativo total superior a R$ 240.000.000,00?",
        "extração mineral e mais de 50% dos ativos da empresa são inerentes estritamente a essas atividades?",
        "Possui patrimônio:",
        "PPE ou PEP*",
        "Sicredi Cheque Empresarial",
        "Talão de Cheque",
        'Caso escolhida a opção "SIM", assinalar:',
        "Canais",
        "Declaração de propósito",
    ]

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        print("PDF aberto com sucesso!")

    def salvar(self, caminho):
        self.doc.save(caminho)
        self.doc.close()

    def _buscar_texto(self, page, texto, clip=None):
        partes = [linha.strip() for linha in texto.splitlines() if linha.strip()]
        buscas = [texto] if "\n" not in texto else [texto, *partes]

        for busca in buscas:
            resultado = page.search_for(busca, clip=clip)
            if resultado:
                return resultado

        return []

    def _normalizar_campo(self, grupo):
        if isinstance(grupo, Campo):
            return grupo

        return Campo(
            ancora=grupo["ancora"],
            tipo=grupo.get("tipo", "checkbox"),
            valor=grupo.get("valor", grupo.get("respostas", [])),
        )

    def localizar_ancora(self, ancora):
        logger.info("Localizando âncora: %s", ancora)

        for numero, page in enumerate(self.doc):
            resultado = sorted(self._buscar_texto(page, ancora), key=lambda rect: (rect.y0, rect.x0))

            if resultado:
                logger.info("Âncora encontrada na página %s", numero + 1)
                return page, resultado[0], numero

        return None, None, None

    def localizar_proxima_ancora(self, ancora_atual, pagina_atual, ancora_rect):
        candidatas = []
        for ancora in self.ORDEM_ANCORAS:
            if ancora == ancora_atual:
                continue

            for numero, page in enumerate(self.doc):
                for rect in self._buscar_texto(page, ancora):
                    if numero < pagina_atual:
                        continue

                    if numero == pagina_atual and rect.y0 <= ancora_rect.y1:
                        continue

                    candidatas.append((numero, rect.y0, page, rect, ancora))

        if not candidatas:
            return None, None, None

        numero, _, page, rect, ancora = sorted(candidatas, key=lambda item: (item[0], item[1]))[0]
        logger.info("Próxima âncora: %s na página %s", ancora, numero + 1)
        return page, rect, numero

    def criar_janela(self, page, ancora_rect, proxima_page=None, proxima_rect=None):
        limite_inferior = page.rect.height

        if proxima_page is page and proxima_rect is not None:
            limite_inferior = proxima_rect.y0

        return fitz.Rect(
            0,
            ancora_rect.y0,
            page.rect.width,
            limite_inferior,
        )

    def obter_opcoes_da_janela(self, page, janela, respostas):
        opcoes = {}
        respostas_unicas = dict.fromkeys(resposta for resposta in respostas if resposta)

        for texto in respostas_unicas:
            ocorrencias_adicionadas = set()
            ocorrencias = self._buscar_texto(page, texto, clip=janela)

            for rect in ocorrencias:
                centro = fitz.Point(
                    (rect.x0 + rect.x1) / 2,
                    (rect.y0 + rect.y1) / 2,
                )

                if janela.contains(centro):
                    chave_rect = (
                        round(rect.x0, 2),
                        round(rect.y0, 2),
                        round(rect.x1, 2),
                        round(rect.y1, 2),
                    )
                    if chave_rect in ocorrencias_adicionadas:
                        continue

                    ocorrencias_adicionadas.add(chave_rect)
                    opcoes.setdefault(texto, []).append(rect)

        for texto in opcoes:
            opcoes[texto].sort(key=lambda rect: (rect.y0, rect.x0))

        return opcoes

    def localizar_checkbox(self, page, texto_rect, janela=None, tolerancia_y=6):
        checkboxes = page.search_for("( )", clip=janela)
        melhor_checkbox = None
        menor_distancia = float("inf")
        texto_centro_y = (texto_rect.y0 + texto_rect.y1) / 2

        for checkbox in checkboxes:
            checkbox_centro_y = (checkbox.y0 + checkbox.y1) / 2
            mesma_linha = abs(checkbox_centro_y - texto_centro_y) <= tolerancia_y

            if not mesma_linha or checkbox.x1 >= texto_rect.x0:
                continue

            distancia = texto_rect.x0 - checkbox.x1
            if distancia < menor_distancia:
                menor_distancia = distancia
                melhor_checkbox = checkbox

        return melhor_checkbox

    def marcar_checkbox(self, page, checkbox_rect):
        centro_x = (checkbox_rect.x0 + checkbox_rect.x1) / 2
        centro_y = (checkbox_rect.y0 + checkbox_rect.y1) / 2

        page.insert_text(
            (centro_x - 3, centro_y + 4),
            "X",
            fontsize=10,
        )
        

    def preencher_ppe_tabela(self, campo):
        page, header_ppe, pagina = self.localizar_ancora("PPE/PEP*")
        if page is None:
            logger.warning("Cabeçalho PPE/PEP* não encontrado.")
            return False

        _, proxima_rect, _ = self.localizar_proxima_ancora(
            "Capital e Cotistas / Acionistas",
            pagina,
            header_ppe,
        )
        janela = fitz.Rect(0, header_ppe.y1, page.rect.width, proxima_rect.y0 if proxima_rect else page.rect.height)

        checkboxes = sorted(page.search_for("( )", clip=janela), key=lambda rect: (rect.y0, rect.x0))
        linhas = {}
        for checkbox in checkboxes:
            chave_linha = round(checkbox.y0)
            linhas.setdefault(chave_linha, []).append(checkbox)

        primeira_linha = next((sorted(linha, key=lambda rect: rect.x0) for linha in linhas.values() if len(linha) >= 4), None)
        if not primeira_linha:
            logger.warning("Checkboxes da tabela PPE/PEP não encontrados.")
            return False

        respostas = campo.valor
        if len(respostas) >= 1:
            self.marcar_checkbox(page, primeira_linha[0 if respostas[0].lower() == "sim" else 1])
        if len(respostas) >= 2:
            self.marcar_checkbox(page, primeira_linha[2 if respostas[1].lower() == "sim" else 3])

        return True

    def preencher_grupo(self, grupo):
        campo = self._normalizar_campo(grupo)

        if campo.tipo == "ppe_tabela":
            return self.preencher_ppe_tabela(campo)

        page, rect, pagina = self.localizar_ancora(campo.ancora)
        if page is None:
            logger.warning("Âncora não encontrada: %s", campo.ancora)
            return False

        proxima_page, proxima_rect, _ = self.localizar_proxima_ancora(campo.ancora, pagina, rect)
        janela = self.criar_janela(page, rect, proxima_page, proxima_rect)
        opcoes = self.obter_opcoes_da_janela(page, janela, campo.valor)

        sucesso = True
        for resposta in campo.valor:
            if resposta not in opcoes or not opcoes[resposta]:
                logger.warning(
                    "Resposta não encontrada na janela da âncora '%s': %s",
                    campo.ancora,
                    resposta,
                )
                sucesso = False
                continue

            texto_rect = opcoes[resposta].pop(0)
            checkbox_rect = self.localizar_checkbox(page, texto_rect, janela)

            if checkbox_rect is None:
                logger.warning(
                    "Checkbox não encontrado na âncora '%s' para '%s'",
                    campo.ancora,
                    resposta,
                )
                sucesso = False
                continue

            self.marcar_checkbox(page, checkbox_rect)

        return sucesso
