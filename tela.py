import customtkinter as ctk
import json
from pathlib import Path
from tkinter import filedialog
from dataclasses import asdict
from preencher_pdf import AnchorPdfFiller, Campo

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class TelaPrincipal(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Gerador de Proposta Sicredi - Completo")
        self.geometry("950x850")
        self.pdf_path = ctk.StringVar(value="")
        self.criar_tela()

    def criar_tela(self):
        self.frame = ctk.CTkScrollableFrame(self)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        titulo = ctk.CTkLabel(
            self.frame,
            text="Gerador de Proposta Sicredi",
            font=("Arial", 26, "bold")
        )
        titulo.pack(pady=20)

        self.criar_seletor_pdf()
        self.criar_perguntas_cadastrais()
        self.criar_secao_socio_ppe()
        self.criar_secao_financeira_patrimonio()
        self.criar_secao_produtos_canais()
        self.criar_botoes()

    # ====================================================
    def criar_seletor_pdf(self):
        self.criar_titulo_secao("Arquivo PDF")

        frame_pdf = ctk.CTkFrame(self.frame)
        frame_pdf.pack(fill="x", pady=5)

        self.campo_pdf = ctk.CTkEntry(
            frame_pdf,
            textvariable=self.pdf_path,
            placeholder_text="Selecione o PDF que deseja preencher",
        )
        self.campo_pdf.pack(side="left", fill="x", expand=True, padx=(10, 8), pady=10)

        ctk.CTkButton(
            frame_pdf,
            text="Selecionar PDF",
            width=140,
            command=self.selecionar_pdf,
        ).pack(side="left", padx=(0, 10), pady=10)

    def selecionar_pdf(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o PDF",
            filetypes=[("Arquivos PDF", "*.pdf")],
        )

        if caminho:
            self.pdf_path.set(caminho)

    # ====================================================
    def criar_perguntas_cadastrais(self):
        self.criar_titulo_secao("Dados Cadastrais e Regulatórios")

        # 1. Atividade correlata à atividade financeira
        ctk.CTkLabel(
            self.frame, 
            text="A empresa exerce alguma atividade correlata à atividade financeira...",
            wraplength=850, justify="left"
        ).pack(anchor="w", pady=(10, 2))
        self.atividade_fin = ctk.StringVar(value="Não")
        self.criar_radio_sim_nao(self.atividade_fin)

        # 2. Entidade constituída em outro país
        ctk.CTkLabel(
            self.frame, 
            text="Entidade constituída em outro país ou sob leis estrangeiras?",
            wraplength=850, justify="left"
        ).pack(anchor="w", pady=(10, 2))
        self.leis_estrangeiras = ctk.StringVar(value="Não")
        self.criar_radio_sim_nao(self.leis_estrangeiras)

    # ====================================================
    def criar_secao_socio_ppe(self):
        self.criar_titulo_secao("Sócios, PPE/PEP e FATCA")
        
        self.socio_ppe = ctk.StringVar(value="Não")
        self.socio_vinculo_ppe = ctk.StringVar(value="Não")
        
        frame_socio = ctk.CTkFrame(self.frame)

        frame_socio.pack(fill="x", pady=5)
        ctk.CTkLabel(frame_socio, text="É PPE?").pack(side="left", padx=10)
        ctk.CTkRadioButton(frame_socio, text="Sim", variable=self.socio_ppe, value="Sim").pack(side="left")
        ctk.CTkRadioButton(frame_socio, text="Não", variable=self.socio_ppe, value="Não").pack(side="left", padx=(0, 30))
        
        ctk.CTkLabel(frame_socio, text="Possui Vínculo PPE?").pack(side="left", padx=10)
        ctk.CTkRadioButton(frame_socio, text="Sim", variable=self.socio_vinculo_ppe, value="Sim").pack(side="left")
        ctk.CTkRadioButton(frame_socio, text="Não", variable=self.socio_vinculo_ppe, value="Não").pack(side="left")

        # Sócio americano com 25% ou mais
        ctk.CTkLabel(
            self.frame, 
            text="Entidade possui sócio(s) americano com 25% ou mais de participação societária?",
            wraplength=850, justify="left"
        ).pack(anchor="w", pady=(10, 2))
        self.socio_americano = ctk.StringVar(value="Não")
        self.criar_radio_sim_nao(self.socio_americano)

        # Declarações gerais de PPE ou PEP
        ctk.CTkLabel(
            self.frame, 
            text="Declarações Gerais de PPE ou PEP:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(15, 2))
        
        self.declara_nao_ppe = ctk.BooleanVar(value=True)  # Padrão Não
        self.declara_sim_ppe = ctk.BooleanVar(value=False)
        self.declara_nao_vinculo = ctk.BooleanVar(value=True)  # Padrão Não
        self.declara_sim_vinculo = ctk.BooleanVar(value=False)

        ctk.CTkCheckBox(self.frame, text="Não sou pessoa politicamente exposta...", variable=self.declara_nao_ppe).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(self.frame, text="Sim, sou pessoa politicamente exposta...", variable=self.declara_sim_ppe).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(self.frame, text="Não possuo vínculo com uma pessoa politicamente exposta...", variable=self.declara_nao_vinculo).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(self.frame, text="Sim, possuo vínculo com uma pessoa politicamente exposta...", variable=self.declara_sim_vinculo).pack(anchor="w", pady=2)

    # ====================================================
    def criar_secao_financeira_patrimonio(self):
        self.criar_titulo_secao("Dados Financeiros e Patrimônio")

        # Ativo total superior a R$ 240.000.000,00
        ctk.CTkLabel(
            self.frame, 
            text="Ativo total superior a R$ 240.000.000,00?",
            wraplength=850, justify="left"
        ).pack(anchor="w", pady=(10, 2))
        self.ativo_superior = ctk.StringVar(value="Não")
        self.criar_radio_sim_nao(self.ativo_superior)

        # Mais de 50% da receita proveniente de prestação de serviços...
        ctk.CTkLabel(
            self.frame, 
            text="Mais de 50% da receita é proveniente estritamente da prestação de serviços, compra/venda, etc.?",
            wraplength=850, justify="left"
        ).pack(anchor="w", pady=(10, 2))
        self.receita_servicos = ctk.StringVar(value="Não")
        self.criar_radio_sim_nao(self.receita_servicos)

        # Patrimônio / Possui patrimônio
        ctk.CTkLabel(
            self.frame, 
            text="Patrimônio Possui patrimônio:",
            wraplength=850, justify="left"
        ).pack(anchor="w", pady=(10, 2))
        self.possui_patrimonio = ctk.StringVar(value="Não")
        self.criar_radio_sim_nao(self.possui_patrimonio)

    # ====================================================
    def criar_secao_produtos_canais(self):
        self.criar_titulo_secao("Produtos, Canais e Finalidade da Conta")

        # Sicredi Cheque Empresarial
        ctk.CTkLabel(self.frame, text="Sicredi Cheque Empresarial").pack(anchor="w", pady=(10, 2))
        self.cheque_empresarial = ctk.StringVar(value="Sim")
        self.criar_radio_sim_nao(self.cheque_empresarial)

        # Talão de Cheque e Folhas
        ctk.CTkLabel(self.frame, text="Talão de Cheque").pack(anchor="w", pady=(10, 2))
        self.talao_cheque = ctk.StringVar(value="Sim")
        self.criar_radio_sim_nao(self.talao_cheque)

        ctk.CTkLabel(self.frame, text="Quantidade de folhas do talão (Se SIM):").pack(anchor="w", pady=(2, 2))
        self.talao_folhas = ctk.StringVar(value="10")
        frame_folhas = ctk.CTkFrame(self.frame)
        frame_folhas.pack(fill="x", pady=5)
        ctk.CTkRadioButton(frame_folhas, text="Talão 10 folhas", variable=self.talao_folhas, value="10").pack(side="left", padx=10)
        ctk.CTkRadioButton(frame_folhas, text="Talão 20 folhas", variable=self.talao_folhas, value="20").pack(side="left")

        # Canais
        ctk.CTkLabel(self.frame, text="Canais (Assinale as opções desejadas):", font=("Arial", 14, "bold")).pack(anchor="w", pady=(15, 2))
        self.canal_internet = ctk.BooleanVar(value=True)
        self.canal_mobi = ctk.BooleanVar(value=True)
        self.canal_nenhum = ctk.BooleanVar(value=False)
        self.canal_consulta = ctk.BooleanVar(value=True)
        self.canal_transacao = ctk.BooleanVar(value=True)

        ctk.CTkCheckBox(self.frame, text="Sicredi Internet Empresa", variable=self.canal_internet).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(self.frame, text="Sicredi Mobi", variable=self.canal_mobi).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(self.frame, text="Nenhum", variable=self.canal_nenhum).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(self.frame, text="Consulta", variable=self.canal_consulta).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(self.frame, text="Transação", variable=self.canal_transacao).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(self.frame, text="Consulta", variable=self.canal_consulta).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(self.frame, text="Transação", variable=self.canal_transacao).pack(anchor="w", pady=2)

        # Finalidade / Utilização da conta (Checkboxes)
        ctk.CTkLabel(self.frame, text="Finalidade da conta (Assinale as opções de uso):", font=("Arial", 14, "bold")).pack(anchor="w", pady=(15, 2))
        self.fin_movimentacao = ctk.BooleanVar(value=True)
        self.fin_meios_pagto = ctk.BooleanVar(value=True)
        self.fin_investimentos = ctk.BooleanVar(value=True)
        self.fin_emprestimos = ctk.BooleanVar(value=True)
        self.fin_cambio = ctk.BooleanVar(value=False)
        self.fin_mercado_cap = ctk.BooleanVar(value=False)
        self.fin_derivativos = ctk.BooleanVar(value=False)

        ctk.CTkCheckBox(self.frame, text="Movimentação de Conta Corrente", variable=self.fin_movimentacao).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(self.frame, text="Utilização de meios de pagamento", variable=self.fin_meios_pagto).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(self.frame, text="Operações de Investimentos", variable=self.fin_investimentos).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(self.frame, text="Contratação de Empréstimos, Financiamentos...", variable=self.fin_emprestimos).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(self.frame, text="Operações de Câmbio", variable=self.fin_cambio).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(self.frame, text="Operações de Mercado de Capitais e Corporate", variable=self.fin_mercado_cap).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(self.frame, text="Operações de Derivativos*", variable=self.fin_derivativos).pack(anchor="w", pady=2)

    # ====================================================
    # Métodos Auxiliares de Interface
    def criar_titulo_secao(self, texto):
        ctk.CTkLabel(
            self.frame, text=texto, font=("Arial", 18, "bold"), text_color="#1f538d"
        ).pack(anchor="w", pady=(25, 10))

    def criar_radio_sim_nao(self, variavel):
        frame = ctk.CTkFrame(self.frame)
        frame.pack(fill="x", pady=5)
        ctk.CTkRadioButton(frame, text="Sim", variable=variavel, value="Sim").pack(side="left", padx=10)
        ctk.CTkRadioButton(frame, text="Não", variable=variavel, value="Não").pack(side="left")

    def criar_botoes(self):
        self.botao = ctk.CTkButton(
            self.frame, text="GERAR PDF", height=45, font=("Arial", 16, "bold"), command=self.gerar_pdf
        )
        self.botao.pack(pady=40)
        self.status = ctk.CTkLabel(self.frame, text="", font=("Arial", 14))
        self.status.pack()

    # ====================================================
    
    def gerar_pdf(self):
            caminho_pdf_texto = self.pdf_path.get().strip()
            if not caminho_pdf_texto:
                self.status.configure(text="Selecione um PDF antes de gerar.", text_color="red")
                return

            caminho_pdf = Path(caminho_pdf_texto)
            if not caminho_pdf.is_file():
                self.status.configure(text="O PDF selecionado nÃ£o foi encontrado.", text_color="red")
                return

            pasta_downloads = Path.home() / "Downloads"
            if not pasta_downloads.exists():
                pasta_downloads = Path.home()

            caminho_saida = pasta_downloads / "pdf_prenchido.pdf"

            
            dados = {
                "depositario_central": Campo(
                    ancora="Depositário Central, Bolsas ou Entidades de Balcão Organizado?",
                    tipo="checkbox",
                    valor=[self.atividade_fin.get()]
                ),
                "leis_estrangeiras": Campo(
                    ancora="Entidade constituída em outro país ou sob leis estrangeiras?",
                    tipo="checkbox",
                    valor=[self.leis_estrangeiras.get()]
                ),
                "socio_ppe_tabela": Campo(
                    ancora="PPE/PEP*",
                    tipo="ppe_tabela",
                    valor=[self.socio_ppe.get(), self.socio_vinculo_ppe.get()]
                ),
                "socio_americano": Campo(
                    ancora="Entidade possui sócio(s) americano com 25% ou mais",
                    tipo="checkbox",
                    valor=[self.socio_americano.get()]
                ),
                "ativo_superior_240m": Campo(
                    ancora="Ativo total superior a R$ 240.000.000,00?",
                    tipo="checkbox",
                    valor=[self.ativo_superior.get()]
                ),
                "receita_50_servicos": Campo(
                    ancora="extração mineral e mais de 50% dos ativos da empresa são inerentes estritamente a essas atividades?",
                    tipo="checkbox",
                    valor=[self.receita_servicos.get()]
                ),
                "possui_patrimonio": Campo(
                    ancora="Possui patrimônio:",
                    tipo="checkbox",
                    valor=[self.possui_patrimonio.get()]
                ),
                "declaracao_ppe": Campo(
                    ancora="PPE ou PEP*",
                    tipo="checkbox",
                    valor=[
                        texto for marcado, texto in [
                            (self.declara_nao_ppe.get(), "Não sou pessoa politicamente exposta ou pessoa exposta politicamente, nos termos dos normativos em vigor."),
                            (self.declara_sim_ppe.get(), "Sim, sou pessoa politicamente exposta ou pessoa exposta politicamente, nos termos dos normativos em vigor."),
                            (self.declara_nao_vinculo.get(), "Não possuo vínculo com uma pessoa politicamente exposta ou pessoa exposta politicamente."),
                            (self.declara_sim_vinculo.get(), "Sim, possuo vínculo com uma pessoa politicamente exposta ou pessoa exposta politicamente."),
                        ] if marcado
                    ]
                ),
                "sicredi_cheque_empresarial": Campo(
                    ancora="Sicredi Cheque Empresarial",
                    tipo="checkbox",
                    valor=[self.cheque_empresarial.get().upper()]
                ),
                "talao_cheque_adesao": Campo(
                    ancora="Talão de Cheque",
                    tipo="checkbox",
                    valor=[self.talao_cheque.get().upper()]
                ),
                "talao_folhas": Campo(
                    ancora='Caso escolhida a opção "SIM", assinalar:',
                    tipo="checkbox",
                    valor=[f"Talão {self.talao_folhas.get()} folhas"] if self.talao_cheque.get() == "Sim" else []
                ),
                "canais": Campo(
                    ancora="Canais",
                    tipo="canais",
                    valor=[
                        texto for marcado, texto in [
                            (self.canal_internet.get(), "internet"),
                            (self.canal_mobi.get(), "mobi"),
                            (self.canal_nenhum.get(), "nenhum"),
                            (self.canal_consulta.get(), "consulta"),
                            (self.canal_transacao.get(), "Transação"),
                            (self.canal_consulta.get(), "Consulta"),
                            (self.canal_transacao.get(), "Transação"),
                        ] if marcado
                    ]
                ),
                "declaracao_proposito": Campo(
                    ancora="Declaração de propósito",
                    tipo="checkbox",
                    valor=[
                        texto for marcado, texto in [
                            (self.fin_movimentacao.get(), "Movimentação de Conta Corrente (débito / crédito / transferências / depósitos em espécie);"),
                            (self.fin_meios_pagto.get(), "Utilização de meios de pagamento (cheque / cartão de débito / cartão de crédito / cobrança / débito em conta / internet banking / outros)"),
                            (self.fin_investimentos.get(), "Operações de Investimentos;"),
                            (self.fin_emprestimos.get(), "Contratação de Empréstimos, Financiamentos, Repasses e/ ou Operações de Arrendamento Mercantil;"),
                            (self.fin_cambio.get(), "Operações de Câmbio;"),
                            (self.fin_mercado_cap.get(), "Operações de Mercado de Capitais e Corporate;"),
                            (self.fin_derivativos.get(), "Operações de Derivativos*"),
                        ] if marcado
                    ]
                ),
            }

            with open("respostas.json", "w", encoding="utf8") as f:
                json.dump({nome: asdict(campo) for nome, campo in dados.items()}, f, indent=4, ensure_ascii=False)

            try:
                filler = AnchorPdfFiller(caminho_pdf)
                for grupo in dados.values():
                    filler.preencher_grupo(grupo)
                filler.salvar(caminho_saida)
                self.status.configure(text=f"PDF gerado com sucesso em: {caminho_saida}", text_color="green")
                return

                self.status.configure(text="✔ PDF gerado com sucesso!", text_color="green")
            except Exception as e:
                self.status.configure(text=f"❌ Erro ao preencher o PDF: {e}", text_color="red")


if __name__ == "__main__":
    app = TelaPrincipal()
    app.mainloop()
