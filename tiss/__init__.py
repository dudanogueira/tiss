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

    def __init__(self, arquivo, xsd_path=None, plugins_path=None):
        self.arquivo = arquivo
        self.version = None
        self.plugins_path = plugins_path
        self.xsd_path = xsd_path
        self.xsd_valido = False
        self.xsd_erros = []
        self.valido = False
        self.erros = {
            'lote': {},
            'guias': {},
        }
        self.arquivo_xsd = None
        # analisa o arquivo
        self.parse()
        if self.arquivo_xsd:
            # descobre versao
            self.get_version()
            if self.version:
                # valida o xsd
                self.xsd_validate()
                if self.xsd_valido:
                    # valida o arquivo
                    self.tiss_validate()
                    # executa plugins do lote
                    #self.executa_plugins()
                    

        xml_errors = None

    def parse(self):
        self.root = etree.fromstring(open(self.arquivo).read())
        self.tipo_transacao = self.root.xpath(
            '//ans:tipoTransacao', namespaces=self.root.nsmap)[0].text
        if self.tipo_transacao == 'ENVIO_LOTE_GUIAS':
            self.arquivo_xsd = 'tiss'

        if not self.arquivo_xsd:
            self.valido = False
            self.erros['lote']['_tipo_transacao'] = 'Tipo de Transação não identificado ou não suportado: %s' % self.tipo_transacao
        
        try:
            self.guias = self.root.xpath('//ans:guiasTISS', namespaces=self.root.nsmap)[0].getchildren()
        except IndexError:
            self.erros['lote']['_guias_inacessiveis'] = u"Não foi possível extrair guias"

    def get_version(self):
        try:
            self.version = self.root.xpath(
                '//ans:versaoPadrao', namespaces=self.root.nsmap)[0].text
        except:
            self.valid = False
            self.errors.append("Não foi possível determinar a versão TISS")

    def xsd_validate(self):

        if not self.xsd_path:
            xsd_file = 'xsd/%sV%s.xsd' % (self.arquivo_xsd, self.version.replace('.', '_'))
            self.xsd_path = os.path.join(os.path.dirname(__file__), xsd_file)
        f = open(self.xsd_path)
        self.root_xsd = etree.parse(f)
        try:
            self.xsd_schema = etree.XMLSchema(self.root_xsd)
            self.xsd_valido = True
        except etree.XMLSchemaParseError, xsd_erros:
            self.xsd_valido = False
            self.xsd_erros = xsd_erros.error_log
            self.erros['lote']['_xsd_invalido'] = u'XSD Inválido!'

    def tiss_validate(self):
        try:
            self.xsd_schema.assertValid(self.root)
            self.valido = True
            self.calcula_hash()
            self.valida_hash()
        except etree.DocumentInvalid, xml_errors:
            self.valid = False
            self.erros['lote']['_xsd'] = xml_errors.error_log

    def calcula_hash(self):
        # remove epilogo do calculo
        self.root_no_epilogo = self.root
        self.epilogo = self.root_no_epilogo.xpath(
            '//ans:epilogo', namespaces=self.root_no_epilogo.nsmap)[0]
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
        print "Executando plugins"
        self.manager = PluginManager()
        if not self.plugins_path:
            self.plugins_path = os.path.join(os.path.dirname(__file__), 'plugins')
        self.manager.setPluginPlaces([self.plugins_path])
        self.manager.collectPlugins()
        print self.manager.getAllPlugins()
        for plugin in self.manager.getAllPlugins():
            plugin.plugin_object.executa(self)
    
    def registra_erro_guia(self, numero, texto):
        try:
            self.erros['guias'][numero]
        except KeyError:
            self.erros['guias'][numero] = []
        self.erros['guias'][numero].append(texto)