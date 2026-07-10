from preencher_pdf import AnchorPdfFiller
import json

with open("respostas.json", encoding="utf8") as f:

    dados = json.load(f)

filler = AnchorPdfFiller(
    "entrada/proposta.pdf"
)

print("PDF aberto com sucesso!")
print(f"Total de páginas: {len(filler.doc)}")

for grupo in dados.values():

    if grupo["tipo"] == "ignorar":
        continue

    filler.preencher_grupo(grupo)

filler.salvar(
    "saida/preenchido.pdf"
)