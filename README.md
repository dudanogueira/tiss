# TISS PARSER
Análise e Validação do Padrão TISS da ANS

Uso:
```
>> from tiss import Tiss
>> t = Tiss("arquivo-valido.xml")
>> t.valido
True

>> t = Tiss("arquivo_invalido.xml")
>> t.valido
False
>> t.tiss_erro
"Erro apresentado"
```

## Validações Realizadas
- Identifica a versao do TISS
- Valida a estrutura com base no Schema XSD da ANS
- Calcula e valida o hash
