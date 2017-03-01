# -*- coding: utf-8 -*-
from yapsy.IPlugin import IPlugin
import datetime
import pymssql


class PluginModelo(IPlugin):
    '''
    Retorna provider de senhas do prestador para checagens
        - Senha (indice)
        - Cod Beneficiario
        - Procedimentos: list com todos aprovados
    '''
    name = "PROVIDER SENHA"

    def executa(self, objeto):
        print('''
        #
        # Executando: %s
        #
        ''' % self.name)
        # para todas as senhas da guia
        senhas = [ i.text for i in objeto.root.xpath("//ans:senha", namespaces=objeto.root.nsmap)]
        # provider a ser registrado
        provider = {}
        try:
            provider_conf = objeto.provider_conf['cardio']
            servidor = provider_conf['servidor']
            usuario = provider_conf['usuario']
            senha = provider_conf['senha']
            conn = pymssql.connect(servidor, usuario, senha, "CARDIO", as_dict=True)
            cursor = conn.cursor()
            query = '''
            select
            	SolicitacaoServico.Codigo as senha,
	            SolicitacaoServico.BenefCodigoCartao as carteira,
	            COUNT(ItemSolServico.AutoId) as procedimentos
	        from SolicitacaoServico
                inner join ItemSolServico on ItemSolServico.Solicitacao=SolicitacaoServico.AutoId
                
            where 
	            SolicitacaoServico.Codigo in (%s)
            group by 
                SolicitacaoServico.Codigo,
                SolicitacaoServico.BenefCodigoCartao
            ''' % ",".join(senhas)
            print(query)
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                senha = row['senha']
                carteira = row['carteira']
                procedimentos = row['procedimentos']
                # para cada um
                # conecta no Cardio e Puxa os dados
                dados = {
                    "carteira" : '0'+str(carteira),
                    "procedimentos" : procedimentos,
                }
                provider[senha] = dados
                objeto.registra_provider('senha', provider)
        except KeyError:
            print(u"Erro! Provider Conf do Cardio não encontrado!")