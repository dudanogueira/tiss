# -*- coding: utf-8 -*-
from yapsy.IPlugin import IPlugin

class CarteiraUnimed(IPlugin):
    name = "CARTEIRA UNIMED"

    def executa(self, objeto):
        print('''
        #
        # Executando PLUGIN: %s
        #
        ''' % self.name)
        # das guias do objeto
        for guia in objeto.guias:
            # aqui usa o xpath com o . antes pra indicar que a busca e dentro do elemento guia
            # objeto.nsmap é o namespace da ANS
            numero = guia.xpath('.//ans:numeroGuiaPrestador', namespaces=objeto.nsmap)[0].text
            carteira = guia.xpath('.//ans:numeroCarteira', namespaces=objeto.nsmap)[0].text
            if carteira.isdigit():
                # carteira nao tem 17 digitos
                if len(carteira) != 17:
                    erro = {
                        'numero': numero,
                        'tag': 'ans:numeroCarteira',
                        'mensagem': "Quantidade de caracteres da CARTEIRA UNIMED deve ser igual a 17"
                    }
                    objeto.registra_erro_guia(erro)
                else:
                    if not mod11_unimed(carteira[1:-1]) == carteira[1:]:
                        erro = {
                            'numero': numero,
                            'tag': "ans:numeroCarteira",
                            'mensagem': u"Dígito Verificador da CARTEIRA UNIMED incorreto."
                        }
                        objeto.registra_erro_guia(erro)
            else:
                erro = {
                        'numero': numero,
                        'tag': 'ans:numeroCarteira',
                        'mensagem': "CARTEIRA UNIMED deve ser somente dígitos."
                    }
                objeto.registra_erro_guia(erro)

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