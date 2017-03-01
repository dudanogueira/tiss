# -*- coding: utf-8 -*-
from yapsy.IPlugin import IPlugin
import datetime
import random


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
        beneficiarios_unicos = set([ i.text for i in objeto.root.xpath("//ans:numeroCarteira", namespaces=objeto.root.nsmap)])
        provider = {}
        for codigo in beneficiarios_unicos:
            # para cada um
            if codigo != "00060501507289096":
                # conecta no Cardio e Puxa os dados
                dados = {
                    "nome" : "Nome do Beneficiario %s"  % codigo,
                    "sexo" : "M",
                    "nascimento" : datetime.date.today() + datetime.timedelta(days=random.randrange(20000)*-1)
                }
                provider[codigo] = dados
            objeto.registra_provider('beneficiario', provider)