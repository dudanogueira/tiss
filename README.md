# TISS PARSER
Análise e Validação do Padrão TISS da ANS

Instalação (breve):

pip install tiss

Uso:
```
>> from tiss import Parser
>> t = Parser("arquivo-valido.xml")
>> t.valido
True

>> t = Parser("arquivo_invalido.xml")
>> t.valido
False
>> t.tiss_erro
["Erro apresentado"]
```

## Validações Realizadas
- Identifica a versao do TISS
- Valida a estrutura com base no Schema XSD da ANS
- Calcula e valida o hash

## ROADMAP
- Permitir plugins para validacao de carteirinha, e confronto com base de dados
- Melhorar sistema de logs, permitindo modo verboso
- Outros