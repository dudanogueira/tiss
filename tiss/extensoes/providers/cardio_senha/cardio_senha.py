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
        print '''
        #
        # Executando: %s
        #
        ''' % self.name
        # para todas as senhas da guia
        senhas = [ i.text for i in objeto.root.xpath("//ans:senha", namespaces=objeto.root.nsmap)]
        # provider a ser registrado
        provider = {}
        if objeto.provider_conf:
            servidor = objeto.provider_conf['cardio']['servidor']
            usuario = objeto.provider_conf['cardio']['usuario']
            senha = usuario = objeto.provider_conf['cardio']['senha']
            print servidor
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
            print query
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                senha = row['senha']
                carteira = row['carteira']
                procedimentos = row['procedimentos']
                # para cada um
                # conecta no Cardio e Puxa os dados
                dados = {
                    "carteira" : carteira,
                    "procedimentos" : procedimentos,
                }
            provider[senha] = dados
        objeto.registra_provider('senha', provider)