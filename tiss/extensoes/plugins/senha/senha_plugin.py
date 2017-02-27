# -*- coding: utf-8 -*-
from yapsy.IPlugin import IPlugin


class PluginModelo(IPlugin):
    name = "SENHA"

    def executa(self, objeto):
        print '''
        #
        # Executando PLUGIN: %s
        #
        ''' % self.name
        senhas = [i.text for i in objeto.root.xpath(
            "//ans:senha", namespaces=objeto.root.nsmap)]
        senhas_unicas = []
        for guia in objeto.guias:
            # pega a senha dessa guia
            senha = guia.xpath(
                ".//ans:senha", namespaces=objeto.root.nsmap)[0].text
            numero = guia.xpath('.//ans:numeroGuiaPrestador',
                                namespaces=guia.nsmap)[0].text
            carteira = guia.xpath('.//ans:numeroCarteira', namespaces=guia.nsmap)[0].text
            # senha ainda nao usada nessa guia
            if senha not in senhas_unicas:
                senhas_unicas.append(senha)
                # confere  com senhas disponiveis no provider

            # senha ja usada nessa guia
            else:
                erro = {
                    'numero': numero,
                    'tag': "//ans:senha",
                    'mensagem': u"Senha %s já utilizada em outra guia" % senha
                }
                objeto.registra_erro_guia(erro)
