# -*- coding: utf-8 -*-
from yapsy.IPlugin import IPlugin

import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('yapsy').setLevel(logging.DEBUG)


def mod11_unimed(a):
    '''
    202208506315300 -> 2022085063153003
    '''
    cross = sum([int(val)*[2,3,4,5,6,7,8,9][idx%8] for idx,val in enumerate(list(str(a))[::-1])])
    #return "%s%s" % (a,cross % 11 == 10 and '-' or 11-(cross % 11))
    digito = 11-(cross%11)
    if digito > 9:
        digito = 0
    return "%s%s" % (a, digito)

def calc_check_digit(number, factors = "86423597"):
    sum = 0
    for (f,n) in zip(factors, number):
        sum += int(f)*int(n)
    chk =  sum % 11
    if chk == 0:
        return 5
    if chk == 1:
        return 0
    return 11 - chk

class CarteiraUnimed(IPlugin):
    name = "Carteira Unimed"

    def executa(self, objeto):
        print "Executando: %s" % self.name
        for guia in objeto.guias:
            numero_guia = guia.xpath('.//ans:numeroGuiaPrestador', namespaces=objeto.root.nsmap)[0].text
            numero_carteira = guia.xpath('.//ans:numeroCarteira', namespaces=guia.nsmap)[0].text
            if len(numero_carteira) != 17:
                objeto.registra_erro_guia(numero_guia, u"Quantidade de Caracteres deve ser igual a 17")
            else:
                if not mod11_unimed(numero_carteira[1:-1]) == numero_carteira[1:]:
                    objeto.registra_erro_guia(numero_guia, u"Dígito Verificador da Carteirinha está errado.")
