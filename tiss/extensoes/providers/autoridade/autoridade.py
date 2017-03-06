from yapsy.IPlugin import IPlugin

class PluginModelo(IPlugin):
    
    name = "Autoridades do Lote."

    def executa(self, objeto):
        '''
        Provê informações básicas do receptor e emissor do lote
        '''
        print('''
        #
        # Executando: %s
        #
        ''' % self.name)
        # busca configuracao no providers conf
        try:
            provider_conf = objeto.provider_conf['autoridade']
            # registra integralmente
            objeto.registra_provider('autoridade', provider_conf)
        except KeyError:
            print(u"Erro! Provider Conf da Autoridade não encontrado!")
