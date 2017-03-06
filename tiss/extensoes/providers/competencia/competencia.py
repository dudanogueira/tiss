# -*- coding: utf-8 -*-
from yapsy.IPlugin import IPlugin

class PluginModelo(IPlugin):
    
    name = "Competencia do Lote."

    def executa(self, objeto):
        '''
        Provê informações básicas da competencia do lote:

        reconhecimento_inicio - inicio do perido de reconhecimento de guias
        reconhecimento_fim - fim do perido de reconhecimento de guias
        '''
        print('''
        #
        # Executando: %s
        #
        ''' % self.name)
        # busca configuracao no providers conf
        try:
            provider_conf = objeto.provider_conf['competencia']
            # registra integralmente
            objeto.registra_provider('competencia', provider_conf)
        except KeyError:
            print(u"Erro! Provider Conf da Competencia não encontrado!")
