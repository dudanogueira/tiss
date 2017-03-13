# -*- coding: utf-8 -*-
from yapsy.IPlugin import IPlugin
import datetime
import pymssql


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
        beneficiarios_unicos = set([ "'%s'" % i.text for i in objeto.root.xpath("//ans:numeroCarteira", namespaces=objeto.nsmap)])
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
        
        provider_conf = objeto.provider_conf['cardio']
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