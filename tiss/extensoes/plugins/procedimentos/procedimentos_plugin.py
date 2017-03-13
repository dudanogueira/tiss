# -*- coding: utf-8 -*-
from yapsy.IPlugin import IPlugin


class PluginModelo(IPlugin):
    name = "PROCEDIMENTOS"

    def executa(self, objeto):
        print('''
        #
        # Executando PLUGIN: %s
        #
        ''' % self.name)
        
        try:
            procedimentos = objeto.providers['procedimentos']
            procedimentos_provider = procedimentos[0]

        except KeyError:
            print("         INFO! Não  foi encontrado o PROVIDER_PROCEDIMENTOS para análise!")
            return False
        if procedimentos_provider:
            for guia in objeto.guias:
                numero = guia.xpath('.//ans:numeroGuiaPrestador',
                    namespaces=objeto.nsmap)[0].text
                # print("#" * 10)
                # print("NUMERO DA GUIA: %s" % numero)
                #para cada procedimento
                for procedimento in guia.xpath('.//ans:procedimento', namespaces=guia.nsmap):
                    tabela = procedimento.xpath('.//ans:codigoTabela', namespaces=guia.nsmap)[0].text
                    codigo = procedimento.xpath('.//ans:codigoProcedimento', namespaces=guia.nsmap)[0].text
                    try:
                        procedimento_cardio = procedimentos_provider[codigo]
                        if not str(procedimento_cardio['tabela']) == str(tabela):
                            erro = {
                                'numero': numero,
                                'tag': "ans:codigoTabela",
                                'mensagem': u"Procedimento %s foi indicado numa tabela diferente da negociada: (%s)" % (codigo, procedimento_cardio['tabela'])
                            }
                            objeto.registra_erro_guia(erro)    
                
                    except KeyError:
                        erro = {
                            'numero': numero,
                            'tag': "ans:codigoProcedimento",
                            'mensagem': u"Procedimento %s não negociado para este prestador" % codigo
                        }
                        objeto.registra_erro_guia(erro)