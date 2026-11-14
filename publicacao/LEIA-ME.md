# Publicação dos dados abertos

Gerada por `publicacao.py`. Dois conjuntos, cada um com a licença da sua fonte (CC BY 4.0 e ODbL 1.0).

1. **Kaggle:** troque `SEU_USUARIO_KAGGLE` pelo seu usuário em cada `kaggle/*/dataset-metadata.json` e rode `kaggle datasets create -p publicacao/kaggle/<pasta>`. Nas semanas seguintes: `kaggle datasets version -p publicacao/kaggle/<pasta> -m "atualização semanal"`. O token (`KAGGLE_KEY`) NUNCA vai para o repositório.
2. **Hugging Face:** crie um dataset por pasta de `huggingface/` e envie o `README.md` e o CSV. O token fica fora do repositório.
3. **dados.gov.br:** copie os campos de `dados-gov-br/cadastro.md`.
