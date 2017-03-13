# -*- coding: utf-8 -*-
from yapsy.IPlugin import IPlugin


class PluginModelo(IPlugin):
    name = "SENHA"

    def executa(self, objeto):
        print('''
        #
        # Executando PLUGIN: %s
        #
        ''' % self.name)
        senhas = [i.text for i in objeto.root.xpath(
            "//ans:senha", namespaces=objeto.nsmap)]
        senhas_unicas = []
        #
        # este plugin espera o provider SENHA para análise
        #
        try:
            senhas_provider = objeto.providers['senha']
        except KeyError:
            print("         INFO! Não  foi encontrado o PROVIDER_SENHA para análise!")
            return False
        if senhas_provider:
            for guia in objeto.guias:
                numero = guia.xpath('.//ans:numeroGuiaPrestador',
                    namespaces=objeto.nsmap)[0].text
                # print("#" * 10)
                # print("NUMERO DA GUIA: %s" % numero)
                # pega a senha dessa guia
                senha_tag = guia.xpath(
                    ".//ans:senha", namespaces=objeto.nsmap)
                if senha_tag:
                    senha = senha_tag[0].text
                    carteira = guia.xpath(
                        './/ans:numeroCarteira', namespaces=objeto.nsmap)[0].text
                    # senha ainda nao usada nessa guia
                    if senha not in senhas_unicas:
                        senhas_unicas.append(senha)

                        # senha ja usada nessa guia
                    else:
                        erro = {
                            'numero': numero,
                            'tag': "ans:senha",
                            'mensagem': u"Senha (%) já utilizada em outra guia." % senha
                        }
                        objeto.registra_erro_guia(erro)

                    # confere  com senhas disponiveis no provider
                    try:
                        carteira_senha = objeto.providers['senha'][0][str(senha)]['carteira']
                        if not int(carteira_senha) == int(carteira):
                            erro = {
                                'numero': numero,
                                'tag': "ans:senha",
                                'mensagem': u"Senha informada (%s) não percente a este beneficiário. (%s)" % (
                                    senha, carteira
                                )
                            }
                            objeto.registra_erro_guia(erro)

                    except (KeyError, IndexError, ValueError):
                        erro = {
                            'numero': numero,
                            'tag': "ans:senha",
                            'mensagem': u"Senha (%s) não encontrada no Sistema Autorizador." % senha
                        }
                        objeto.registra_erro_guia(erro)
                else:
                    erro = {
                        'numero': numero,
                        'tag': "ans:senha",
                        'mensagem': u"Senha não pode ser definida/encontrada."
                    }
                    objeto.registra_erro_guia(erro)