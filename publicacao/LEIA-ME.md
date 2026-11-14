# Publicação dos dados abertos

Gerada por `publicacao.py`. Dois conjuntos, cada um com a licença da sua fonte (CC BY 4.0 e ODbL 1.0).

1. **Kaggle:** os dois datasets já foram criados em 14/11/2026 (veja os links em `/dados-abertos`). Para atualizar, rode `kaggle datasets version -p publicacao/kaggle/<pasta> -m "atualização semanal"` com o token em variável de ambiente (`KAGGLE_API_TOKEN` ou `KAGGLE_KEY`), NUNCA no repositório. O título tem no máximo 50 caracteres e o subtítulo no máximo 80 (limites do Kaggle).
2. **Hugging Face:** crie um dataset por pasta de `huggingface/` e envie o `README.md` e o CSV. O token fica fora do repositório.
3. **dados.gov.br:** copie os campos de `dados-gov-br/cadastro.md`.
