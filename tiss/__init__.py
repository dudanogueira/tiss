# -*- coding: utf-8 -*-
#! /usr/bin/python
from lxml import etree
from yapsy.PluginManager import PluginManager
import os
import hashlib

import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('yapsy').setLevel(logging.DEBUG)


__author__ = 'Duda Nogueira'
__version__ = '0.0.1'
__license__ = 'MIT'

class Parser(object):

    def __init__(
            self, 
            arquivo,
            provider_conf = {},
            xsd_path=None, 
            plugins_path=None, 
            providers_path=None,
            skeep=False
        ):
        self.provider_conf = provider_conf
        self.arquivo = arquivo
        self.version = None
        self.skeep_validation = skeep 
        self.plugins_path = plugins_path
        self.providers_path = providers_path
        self.xsd_path = xsd_path
        self.xsd_valido = False
        self.xsd_erros = []
        self.valido = False
        self.erros = {
            'lote': {},
            'guias': {},
        }
        self.providers = {}
        self.arquivo_xsd = None
        # analisa o arquivo
        if not self.skeep_validation:
            self.parse()
            if self.arquivo_xsd:
            #     # descobre versao
                self.get_version()
                if self.version:
                    # valida o xsd
                    self.xsd_validate()
                    if self.xsd_valido:
                        # validação estrutural
                        self.valida_estrutura()
                        if self.valido:
                            # executa plugins de providers
                            self.executa_providers()
                            # validação do negócios em modelo de plugins
                            self.executa_plugins()
                            # se existir erros de guia, marca lote invalido
                            guias_invalidas = len(self.erros['guias'].items())
                            inconsistencias = 0
                            if guias_invalidas:
                                for guia in self.erros['guias'].items():
                                    inconsistencias += len(guia[1])
                                self.valido = False
                                self.erros['lote']['_guias'] = u"%s Guias apresentaram %s inconsistências" % (
                                    guias_invalidas,
                                    inconsistencias
                                )
                        else:
                            self.erros['lote']['_estrutura'] = "Estrutura não é válida"
                        

            xml_errors = None

    def parse(self):
        #
        # tenta identar o XML para apontar erro em linha
        conteudo = open(self.arquivo, encoding='iso-8859-1').read()
        # remove o encoding do xml para deixar o lxml trabalhar
        conteudo_sem = conteudo.replace('encoding="iso-8859-1"', '')
        root = etree.fromstring(conteudo_sem)
        # conteudo bonito, identado
        cb = etree.tostring(root, pretty_print=True).decode()
        self.root = etree.fromstring(cb)

        # checa se namespace valido.
        # namespace errado da erro de interpretação.
        try:
            # se nao possuir o esquema da ans no namespace
            # forçar definir hardcoded.
            self.nsmap = self.root.nsmap
            self.schema_ans_url = self.nsmap['ans']
        except KeyError:
            self.nsmap = {
                'ans': 'http://www.ans.gov.br/padroes/tiss/schemas',
                'ds': 'http://www.w3.org/2000/09/xmldsig#',
                'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
            }
            # devoler pro root o nsmap forçado
            #self.root.nsmap = self.nsmap
        
        # define o tipo de trasacao
        self.tipo_transacao = self.get_xpath(
            '//ans:tipoTransacao'
            )[0].text.replace("\n", '').replace("\t", '')

        # no momento so suporta envio de lote
        if self.tipo_transacao == 'ENVIO_LOTE_GUIAS':
            # neste caso, o arquivo xsd é  o tiss, dentro da pasta xsd
            self.arquivo_xsd = 'tiss'
            # tambem existe um numero do lote
            self.numero_lote = self.get_xpath("//ans:numeroLote")[0].text
            # numero sequencial
            self.numero_sequencial = self.get_xpath("//ans:sequencialTransacao")[0].text
        #
        # aqui precisa fazer testes em outros tipos de transação
        #  deve ser possivel/necessario filtrar isso nos plugins e providers
        #

        

        # arquivo xsd não encontrado.
        if not self.arquivo_xsd:
            self.valido = False
            self.erros['lote']['_transacao'] = 'Tipo de Transação não identificado ou não suportado: %s' % self.tipo_transacao
        
        # extrai as guias para utilizacao nos plugins
        self.guias = self.root.xpath('//ans:guiasTISS', namespaces=self.nsmap)[0].getchildren()

        # extrai o prestador do lote
        #self.codigo_prestador =  self.get_xpath(
        #        "//ans:cabecalho//ans:codigoPrestadorNaOperadora"
        #)[0].text

    def get_version(self):
        '''retorna versao no formato N.NN.NN, conforme xml
        '''
        try:
            # versao 3.0.1
            versao301 = self.get_xpath(
                '//ans:Padrao'
            )
            if versao301:
                self.version = versao301[0].text
            else:
                self.version = self.get_xpath(
                    '//ans:versaoPadrao'
                )[0].text.replace("\n", '').replace("\t", '')
        except:
            self.valid = False
            self.erros['lote']['_versao'] = u"Erro ao detectar a versão do padrão TISS"

    def xsd_validate(self):

        if not self.xsd_path:
            xsd_file = 'xsd/%sV%s.xsd' % (self.arquivo_xsd, self.version.replace('.', '_'))
            self.xsd_path = os.path.join(os.path.dirname(__file__), xsd_file)
        #f = open(self.xsd_path)
        self.root_xsd = etree.parse(self.xsd_path)
        try:
            self.xsd_schema = etree.XMLSchema(self.root_xsd)
            self.xsd_valido = True
        except etree.XMLSchemaParseError as xsd_erros:
            self.xsd_valido = False
            self.xsd_erros = xsd_erros
            i = 1
            for erro in self.xsd_erros.error_log:
                self.erros['lote']['_xsd_invalido%i' % i] = "Arquivo: %s, Linha %s, Coluna: %s: %s" % (
                    erro.filename, erro.line, erro.column, erro.message
                )
                i += 1

    def valida_estrutura(self):
        try:
            self.xsd_schema.assertValid(self.root)
            self.valido = True
            self.schema_valido = True
            self.calcula_hash()
            self.valida_hash()
        except etree.DocumentInvalid as xml_errors:
            self.valid = False
            self.schema_valido = False
            self.schema_erros = xml_errors
            i = 1
            for erro in self.schema_erros.error_log:
                self.erros['lote']['_schema_invalido%i' % i] = "Linha %s, Coluna: %s: %s" % (erro.line, erro.column, erro.message)
                i += 1

    def calcula_hash(self):
        # remove epilogo do calculo
        self.root_no_epilogo = self.root
        self.epilogo = self.root_no_epilogo.xpath(
            '//ans:epilogo', namespaces=self.nsmap)[0]
        self.root_no_epilogo.remove(self.epilogo)
        self.hash_fornecido = self.epilogo.getchildren()[0].text
        reslist = list(self.root_no_epilogo.iter())
        conteudos = []
        for i in reslist:
            if not i.getchildren():
                conteudos.append(i.text)
        self.conteudo = ''.join(conteudos)
        cod = hashlib.md5()
        cod.update(self.conteudo.encode('iso-8859-1'))
        self.hash = cod.hexdigest()
        self.parse()

    def valida_hash(self):
        if self.hash != self.hash_fornecido:
            self.valido = False
            self.erros['lote']['_hash'] = "Hash Inválido! Fornecido: %s, Calculado: %s" % (
                self.hash_fornecido, self.hash)
    


    def executa_plugins(self, plugin_path=None):
        print("Executando plugins")
        self.plugin_manager = PluginManager()
        self.plugin_manager.setPluginInfoExtension("tiss-plugin")
        if not self.plugins_path:
            self.plugins_path = os.path.join(os.path.dirname(__file__), 'extensoes/plugins')
        self.plugin_manager.setPluginPlaces([self.plugins_path])
        self.plugin_manager.collectPlugins()
        for plugin in self.plugin_manager.getAllPlugins():
            plugin.plugin_object.executa(objeto=self)
    
    def executa_providers(self, providers_path=None):
        print("Executando Providers")
        self.provider_manager = PluginManager()
        self.provider_manager.setPluginInfoExtension("tiss-provider")
        if not self.providers_path:
            self.providers_path = os.path.join(os.path.dirname(__file__), 'extensoes/providers')
        self.provider_manager.setPluginPlaces([self.providers_path])
        self.provider_manager.collectPlugins()
        for plugin in self.provider_manager.getAllPlugins():
            plugin.plugin_object.executa(objeto=self)


    def registra_erro_guia(self, erro):
        try:
            self.erros['guias'][erro['numero']]
        except KeyError:
            self.erros['guias'][erro['numero']] = []
        self.erros['guias'][erro['numero']].append(erro)
    
    def registra_provider(self, provider_name, provider):
        '''
        registra os dados de uma provider
        '''
        try:
            self.providers[provider_name]
        except:
            self.providers[provider_name] = {}
        self.providers[provider_name] = [provider]
    
    def get_xpath(self, xpath):
        return self.root.xpath(xpath, namespaces=self.nsmap)