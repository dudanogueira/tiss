# -*- coding: utf-8 -*-
#! /usr/bin/python
from lxml import etree
import os


import hashlib


class Tiss(object):

    def __init__(self, arquivo, xsd_path=None):
        self.arquivo = arquivo
        self.version = None
        self.xsd_path = xsd_path
        self.xsd_valid = False
        self.xsd_error = None
        self.tiss_valid = False
        self.tiss_error = None
        self.parse()
        self.get_version()
        if self.version:
            self.xsd_validate()
            self.tiss_validate()

    def parse(self):
        self.root = etree.fromstring(open(self.arquivo).read())

    def get_version(self):
        try:
            self.version = self.root.xpath(
                '//ans:versaoPadrao', namespaces=self.root.nsmap)[0].text
        except:
            self.tiss_valid = False
            self.tiss_error = "Couldn't determine the tiss version"

    def xsd_validate(self):
        if not self.xsd_path:
            xsd_file = 'xsd/%s/tissV%s.xsd' % (
                self.version, self.version.replace('.', '_'))
            self.xsd_path = os.path.join(os.getcwd(), xsd_file)
        f = open(self.xsd_path)
        self.root_xsd = etree.parse(f)
        try:
            self.xsd_schema = etree.XMLSchema(self.root_xsd)
            self.xsd_valid = True
        except etree.XMLSchemaParseError as e:
            self._valid = False
            self.xsd_error = e
            exit(1)

    def tiss_validate(self):
        try:
            self.xsd_schema.assertValid(self.root)
            self.tiss_valid = True
            self.calcula_hash()
            self.valida_hash()
        except etree.DocumentInvalid as e:
            self.tiss_valid = False
            self.tiss_error = e

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
    
    def valida_hash(self):
        if self.hash != self.hash_fornecido:
            self.tiss_valid = False
            self.tiss_error = "Hash Inválido! Fornecido: %s, Calculado: %s" % (self.hash_fornecido, self.hash)

