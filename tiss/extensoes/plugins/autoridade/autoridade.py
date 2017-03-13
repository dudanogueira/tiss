# -*- coding: utf-8 -*-
from yapsy.IPlugin import IPlugin

class Autoridaded(IPlugin):
    name = "VALIDACAO DE AUTORIDADE"

    def executa(self, objeto):
        print('''
        #
        # Executando PLUGIN: %s
        #
        ''' % self.name)
        #
        # valida se o lote e pra esta operadora
        #
        try:
            operadora_codigo = objeto.get_xpath(
                    "//ans:destino//ans:registroANS"
                )[0].text
            try:
                autoridade_provider = objeto.providers['autoridade'][0]
                if not str(operadora_codigo) == str(autoridade_provider['operadora']['registroANS']):
                    objeto.erros['lote']['_operadora_codigo'] = "Código da Operadora na ANS informado não pertence a esta Operadora."
                # confere cada guia.
                codigos_guias = [i.text for i in objeto.get_xpath("//ans:guiasTISS//ans:registroANS")]
                if not all(codigo == operadora_codigo for codigo in codigos_guias):
                    objeto.erros['lote']['_guias_destino_errado'] = "Existem guias cujos destinos não são para essa Operadora."
                    # TODO apontar qual guia
            except KeyError:
                print("         INFO! Não  foi encontrado o PROVIDER_AUTORIDADE para análise!")
                return False
        except IndexError:
            objeto.erros['lote']['_operadora_codigo'] = "Código de Destino da Operadora não pôde ser definido."
        #
        # valida se identificacao do prestador bate com provider confs
        # conferencias são por: codigo prestador, cpf ou cnpj
        try:
            identificacao_prestador = objeto.get_xpath("//ans:origem//ans:identificacaoPrestador")[0]
            id_valido = False
            for id in identificacao_prestador:
                try:
                    # pega o nome da tag sem namespace
                    id_tag = id.xpath("local-name()")
                    # tenta buscar no providers de autoridade
                    if not str(objeto.providers['autoridade'][0]['prestador'][id_tag]) == str(id.text):
                        objeto.erros['lote']['_prestador_codigo_%s' % id_tag] = "%s do Prestador de Origem não confere com o cadastro." % id_tag
                    else:
                        id_valido = True
                except KeyError:
                    pass
            if not id_valido:
                objeto.erros['lote']['_prestador_codigo'] = "Não foi possível validar a Origem do Prestador"

        except IndexError:
            objeto.erros['lote']['_prestador_codigo'] = "Código de Origem do Prestador não pôde ser definido."


