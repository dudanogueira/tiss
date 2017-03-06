# TISS PARSER
Análise e Validação do Padrão TISS da ANS

Instalação (breve):

pip install tiss

Uso Simples:
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

Uso 

## Funcionalidades e Validações
- [validacao] Identifica a versao do TISS
- [validacao]  Valida a estrutura com base no Schema XSD da ANS
- [validacao] Calcula e valida o hash
- [funcionalidade] Permite plugins e providers externos

## ROADMAP
- Melhorar sistema de logs, permitindo modo verboso
- Desenhar modelo de plugin Orientado a Objeto, permitindo a criação de testes unitários por guia, etc.
- Escrever testes básicos.