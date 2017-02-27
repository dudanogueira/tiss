# -*- coding: utf-8 -*-
from yapsy.IPlugin import IPlugin



class PluginModelo(IPlugin):
    name = "MODELO"

    def executa(self, objeto):
        print '''
        #
        # Executando PLUGIN: %s
        #
        ''' % self.name
        print u"Nao faço nada!"