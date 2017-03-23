# -*- coding: utf-8 -*-
from yapsy.IPlugin import IPlugin
import datetime
import re

class CarteiraUnimed(IPlugin):
    name = "COMPETENCIA DO LOTE"

    def executa(self, objeto):
        print('''
        #
        # Executando PLUGIN: %s
        #
        ''' % self.name)
        try:
            inicio = objeto.provider_conf['competencia']['reconhecimento_inicio']
            fim = objeto.provider_conf['competencia']['reconhecimento_fim']
        except:
            print("NECESSARIO O PROVIDER DE COMPETENCIA!!!")
            return False
        try:
            beneficiario_provider = objeto.providers['beneficiario'][0]
        except:
            print("NECESSARIO O PROVIDER DE BENEFICIARIO!!!")
            return False
        if objeto.get_xpath("//ans:guiaResumoInternacao"):
            print("GUIAS DE INTERNACAO")
            for guia in objeto.guias:
                carteira_guia = guia.xpath('.//ans:numeroCarteira', namespaces=guia.nsmap)[0].text
                # quando nao consegue recuperar o provider, assumir que nao eh local
                try:
                    local = beneficiario_provider[carteira_guia]['local']
                except KeyError:
                    local = False
                numero = guia.xpath('.//ans:numeroGuiaPrestador',
                        namespaces=objeto.nsmap)[0].text
                # se for internacao, considerar data final da internacao
                data_final = guia.xpath(".//ans:dadosInternacao//ans:dataFinalFaturamento", namespaces=objeto.nsmap)[0].text
                hora_final = guia.xpath(".//ans:dadosInternacao//ans:horaFinalFaturamento", namespaces=objeto.nsmap)[0].text
                dt_final = "%s %s" % (data_final, hora_final)
                dt = datetime.datetime.strptime(dt_final, "%Y-%m-%d %H:%M:%S")
                if not (dt > inicio and dt < fim) and not local:
                    erro = {
                            'numero': numero,
                            'tag': "ans:dataFinalFaturamento", # horaFinalFaturamento
                            'mensagem': u"Data do Final da Internação (%s) para (%s) está fora do período de reconhecimento aceito." % (
                                dt_final, carteira_guia
                            )
                        }
                    objeto.registra_erro_guia(erro)


                    
                    
        else:
            print("GUIAS NORMAIS, CHECAGEM NAO DE INTERNACAO")
            for guia in objeto.guias:
                numero = guia.xpath('.//ans:numeroGuiaPrestador',
                        namespaces=objeto.nsmap)[0].text
                carteira_guia = guia.xpath('.//ans:numeroCarteira', namespaces=guia.nsmap)[0].text
                # quando nao consegue recuperar o provider, assumir que nao eh local
                try:
                    local = beneficiario_provider[carteira_guia]['local']
                except KeyError:
                    local = False
                #datas = [datetime.datetime.strptime(data.text, "%Y-%M-%d") for data in guia.xpath(".//ans:dataExecucao", namespaces=objeto.nsmap)]
                for procedimento in guia.xpath('.//ans:procedimentoExecutado', namespaces=guia.nsmap):
                    data_str = procedimento.xpath('.//ans:dataExecucao', namespaces=guia.nsmap)[0].text
                    codigo = procedimento.xpath('.//ans:codigoProcedimento', namespaces=guia.nsmap)[0].text
                    data = datetime.datetime.strptime(data_str, "%Y-%m-%d")
                    if not (data > inicio and data < fim) and not local:
                        erro = {
                                'numero': numero,
                                'tag': "ans:dataExecucao",
                                'mensagem': u"Data de Execução (%s) do procedimento (%s) para Carteira (%s) está fora do período de reconhecimento aceito." % (
                                    data_str, codigo, carteira_guia
                                )
                            }
                        objeto.registra_erro_guia(erro)
            