# -*- coding: utf-8 -*-
from yapsy.IPlugin import IPlugin
import datetime

class CarteiraUnimed(IPlugin):
    name = "COMPETENCIA DO LOTE"

    def executa(self, objeto):
        print('''
        #
        # Executando PLUGIN: %s
        #
        ''' % self.name)
        inicio = objeto.providers['competencia'][0]['reconhecimento_inicio']
        fim = objeto.providers['competencia'][0]['reconhecimento_fim']
        if objeto.get_xpath("//ans:guiaResumoInternacao"):
            #print("GUIAS DE INTERNACAO")
            for guia in objeto.guias:
                numero = guia.xpath('.//ans:numeroGuiaPrestador',
                        namespaces=objeto.nsmap)[0].text
                # se for internacao, considerar data final da internacao
                data_final = guia.xpath(".//ans:dadosInternacao//ans:dataFinalFaturamento", namespaces=objeto.nsmap)[0].text
                hora_final = guia.xpath(".//ans:dadosInternacao//ans:horaFinalFaturamento", namespaces=objeto.nsmap)[0].text
                dt_final = "%s %s" % (data_final, hora_final)
                dt = datetime.datetime.strptime(dt_final, "%Y-%m-%d %H:%M:%S")
                if not (dt > inicio and dt < fim):
                    erro = {
                            'numero': numero,
                            'tag': "ans:dataFinalFaturamento", # horaFinalFaturamento
                            'mensagem': u"Data do Final da Internação está fora do período de reconhecimento aceito."
                        }
                    objeto.registra_erro_guia(erro)
                    
                    
        else:
            #print("GUIAS NORMAIS, CHECAGEM NAO DE INTERNACAO")
            for guia in objeto.guias:
                numero = guia.xpath('.//ans:numeroGuiaPrestador',
                        namespaces=objeto.nsmap)[0].text
                
                datas = [datetime.datetime.strptime(data.text, "%Y-%M-%d") for data in guia.xpath(".//ans:dataExecucao", namespaces=objeto.nsmap)]

                if not all(d > inicio and d < fim for d in datas):
                    erro = {
                            'numero': numero,
                            'tag': "ans:dataExecucao",
                            'mensagem': u"Data de Execução de Procedimentos está fora do período de reconhecimento aceito."
                        }
                    objeto.registra_erro_guia(erro)
            