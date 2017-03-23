# -*- coding: utf-8 -*-
from yapsy.IPlugin import IPlugin
import datetime
import pymssql
import re

class PluginModelo(IPlugin):
    '''
    Retorna provider do beneficiario para checagens
     - Nome
     - Sexo
     - Nascimento
     - Datas de inativação
    '''
    name = "PROVIDER BENEFICIARIO"

    def executa(self, objeto):
        print('''
        #
        # Executando: %s
        #
        ''' % self.name)
        # para todos os beneficiarios presentes na guia
        carteiras_e = objeto.root.xpath("//ans:numeroCarteira", namespaces=objeto.nsmap)
        carteiras = [e.text for e in carteiras_e]
        beneficiarios_unicos = set([ "'%s'" % re.sub(r"\D", "", i) for i in carteiras])
        provider = {}
        query = '''
        Select 
        	right(replicate('0',17)+cast(codigo as varchar(17)),17) as codigo,
	        left(right(replicate('0',17)+cast(codigo as varchar(17)),17), 4) as operadora,
	        pessoa.Nome as nome,
	        pessoa.Sexo as sexo,
            beneficiario.tipo,
            pessoa.DataNascimento as nascimento
        from beneficiario 
        inner join Pessoa on Beneficiario.Pessoa=Pessoa.AutoId
        where Codigo in (
	        %s
        )
        ''' % ",".join(beneficiarios_unicos)
        try:
            provider_conf = objeto.provider_conf['cardio']
        except:
            print("INFO: provider do Cardio nao encontrado")
            return False
        servidor = provider_conf['servidor']
        usuario = provider_conf['usuario']
        banco = provider_conf['banco']
        senha = provider_conf['senha']
        conn = pymssql.connect(servidor, usuario, senha, banco, as_dict=True)
        print("conectando a banco...")
        cursor = conn.cursor()
        print(query)
        cursor.execute(query)
        rows = cursor.fetchall()

        
        for row in rows:
            # para cada um
            if row['tipo'] != 9:
                local = True
            else:
                local = False
            dados = {
                "nome" : row['nome'],
                "sexo" : row['sexo'],
                "nascimento" : row['nascimento'],
                "operadora" : row['operadora'],
                "codigo" : row['codigo'],
                "local": local
            }
            # atualiza o provider
            provider[row['codigo']] = dados
        # registra global
        objeto.registra_provider('beneficiario', provider)