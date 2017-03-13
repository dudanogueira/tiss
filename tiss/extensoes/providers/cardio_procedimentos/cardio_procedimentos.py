# -*- coding: utf-8 -*-
from yapsy.IPlugin import IPlugin
import datetime
import pymssql


class PluginModelo(IPlugin):
    '''
    Retorna o Provider de procedimentos:
    ex:
    provider['procedimentos'] = {
        '60000775': {
            'tabela': 18,
            'valor': 88.76
        }
    }
    '''
    name = "PROVIDER PROCEDIMENTOS"

    def executa(self, objeto):
        print('''
        #
        # Executando: %s
        #
        ''' % self.name)
        # provider a ser registrado
        provider = {}
        try:
            provider_conf = objeto.provider_conf['cardio']
            servidor = provider_conf['servidor']
            usuario = provider_conf['usuario']
            banco = provider_conf['banco']
            senha = provider_conf['senha']
            classe = objeto.provider_conf['autoridade']['prestador']['classe']
            codigo_prestador = objeto.provider_conf['autoridade']['prestador']['codigoPrestadorNaOperadora']
            print("conectando a banco...")
            conn = pymssql.connect(servidor, usuario, senha, banco, as_dict=True)
            cursor = conn.cursor()
            #
            # classe 5, query especial pra MGHOSP / CATEGORIA HOSPITALAR NO CARDIO
            #
            if classe == 5:
                query = '''
                    Select
                        ServicoOperadora.Codigo as codigo,
                        ServicoOperadora.TipoTabelaServico as tabela,
                        Sum(CompServTabela.Valor) as valor
                        
                    from PrestadorServico
                    left join NegociacaoTabServ on NegociacaoTabServ.ClassePrestador=PrestadorServico.Classe
                    left join NegConjuntoTabela on NegConjuntoTabela.Negociacao=NegociacaoTabServ.AutoId
                    left join ConjuntoTabelaServ on NegConjuntoTabela.ConjTabela=ConjuntoTabelaServ.Codigo
                    left join TabConjTabServico on TabConjTabServico.Conjunto=ConjuntoTabelaServ.Codigo
                    left join TabelaServico on TabConjTabServico.Tabela=TabelaServico.Codigo
                    left join ValorServTabela on ValorServTabela.Tabela=TabelaServico.Codigo and ValorServTabela.FimVigencia is Null
                    left join CompServTabela on CompServTabela.Servico=ValorServTabela.AutoId
                    left join ServicoOperadora on ValorServTabela.Servico=ServicoOperadora.AutoId and ServicoOperadora.FimVigencia is Null

                    where
                        ServicoOperadora.Codigo is not Null and 
                        CodigoReduzido = %s
                    group by 
                        ServicoOperadora.Codigo, 
                        ServicoOperadora.TipoTabelaServico
                    order by 1

                ''' % codigo_prestador
            else:
                query = '''
                    Select
                        ServicoOperadora.Codigo as codigo,
                        ServicoOperadora.TipoTabelaServico as tabela,
                        Sum(CompServTabela.Valor) as valor
                        
                    from PrestadorServico
                    left join NegociacaoTabServ on NegociacaoTabServ.ClassePrestador=PrestadorServico.Classe
                    left join NegConjuntoTabela on NegConjuntoTabela.Negociacao=NegociacaoTabServ.AutoId  and NegConjuntoTabela.Categoria=PrestadorServico.Categoria
                    left join ConjuntoTabelaServ on NegConjuntoTabela.ConjTabela=ConjuntoTabelaServ.Codigo
                    left join TabConjTabServico on TabConjTabServico.Conjunto=ConjuntoTabelaServ.Codigo
                    left join TabelaServico on TabConjTabServico.Tabela=TabelaServico.Codigo
                    left join ValorServTabela on ValorServTabela.Tabela=TabelaServico.Codigo and ValorServTabela.FimVigencia is Null
                    left join CompServTabela on CompServTabela.Servico=ValorServTabela.AutoId
                    left join ServicoOperadora on ValorServTabela.Servico=ServicoOperadora.AutoId and ServicoOperadora.FimVigencia is Null

                    where
                        ServicoOperadora.Codigo is not Null and 
                        CodigoReduzido = %s
                    group by 
                        ServicoOperadora.Codigo, 
                        ServicoOperadora.TipoTabelaServico
                    order by 1

                ''' % codigo_prestador
                
            print(query)
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                codigo = row['codigo']
                tabela = row['tabela']
                valor = row['valor']
                # para cada um
                # conecta no Cardio e Puxa os dados
                dados = {
                    "codigo" : codigo,
                    "tabela" : tabela,
                    "valor": valor
                }
                provider[codigo] = dados
            objeto.registra_provider('procedimentos', provider)
        except KeyError:
            print(u"Erro! Provider Conf do Cardio não encontrado!")