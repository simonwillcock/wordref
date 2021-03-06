# -*- coding: utf-8 -*-

'''
© WordReference.com
© 2011 Michele Lacchia
'''


import sys
import json
import urllib2

from objects import Result, Translation, Term



class WordRefError(Exception):
    '''Base class for all wordref's errors.'''

class ApiError(WordRefError):
    '''Raised when user request cannot be accomplished by the API.'''

class ParsingError(WordRefError):
    '''Raised when errors occur during the parsing.'''


class Api(object):
    def __init__(self, user_id, code, api_version=None):
        self.user_id = user_id
        if len(code) == 2:
            raise ApiError('Monolingual dictionaries are not available yet')
        elif len(code) != 4:
            raise ApiError('Wrong dictionary code')
        elif code == 'esen':
            raise ApiError('Spanish - English dictionary does not support Json API')
        
        self.code = code
        self.api_version = api_version

    def __repr__(self):
        return 'Api(user_id={0}, code={1}, api_version={2})'.format(self.user_id,
                                                                    self.code,
                                                                    self.api_version or 'last')

    def __str__(self):
        return '<Api[{0}] at {1}>'.format(self.code, id(self))

    def search(self, term):
        url = self._build_url(term)
        data = urllib2.urlopen(url).read()
        try:
            return self._parse_result(data)
        except Exception as e:
            try:
                msg = e.args[0]
            except IndexError:
                msg = repr(e)
            raise ParsingError(msg)

    def _build_url(self, term):
        if self.api_version is None:
            base = 'http://api.wordreference.com/{self.user_id}/json/{self.code}/{0}'
        else:
            base = 'http://api.wordreference.com/{self.api_version}/{self.user_id}/json/{self.code}/{0}'
        return base.format(term, self=self)

    def _parse_result(self, data):
        data = json.loads(data)
        result = Result()
        for term, categories in data.iteritems():
            if term in ('Lines', 'END'):
                continue
            for category, translations in data[term].iteritems():
                tr = {}
                for i, trans in translations.iteritems():
                    tr[Translation(trans)] = i
                result.add(category, tuple(sorted(tr.keys(), key=lambda i: tr[i])))
        return result
