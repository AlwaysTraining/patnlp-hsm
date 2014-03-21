'''
Functionality for extracting numberical values on SQL text fields and store them in
related databases.
'''

import MySQLdb
import ast

from hsm.tools.numextractor import NumExtractor


CREATE_SCRIPT = '''
CREATE TABLE IF NOT EXISTS `{SCHEMA}`.`{PREFIX}rr` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `epiId` BIGINT(20) NOT NULL,
  `field` CHAR(32) NOT NULL,
  `systolic` INT NULL,
  `diastolic` INT NULL,
  `pulse` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `rr_field_idx` (`field` ASC),
  INDEX `rr_epiid_idx` (`epiId` ASC))
ENGINE = InnoDB;
'''

# TODO
'''CREATE TABLE IF NOT EXISTS `{SCHEMA}`.`{PREFIX}temp` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `epiId` BIGINT(20) NOT NULL,
  `field` CHAR(32) NOT NULL,
  `temp` DECIMAL(10,0) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `temp_field_idx` (`field` ASC),
  INDEX `temp_epiid_idx` (`epiId` ASC))
ENGINE = InnoDB;

TRUNCATE TABLE `{SCHEMA}`.`{PREFIX}temp`;

CREATE TABLE IF NOT EXISTS `{SCHEMA}`.`{PREFIX}kmi` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `epiId` BIGINT(20) NOT NULL,
  `field` CHAR(32) NOT NULL,
  `weight` DECIMAL(10,0) NULL,
  `height` DECIMAL(10,0) NULL,
  `kmi` DECIMAL(10,0) NULL,
  PRIMARY KEY (`id`),
  INDEX `kmi_field_idx` (`field` ASC),
  INDEX `kmi_epiid_idx` (`epiId` ASC))
ENGINE = InnoDB;

TRUNCATE TABLE `{SCHEMA}`.`{PREFIX}kmi`;
'''

def sql_create_script(schema, prefix):
    '''Function that returns the SQL create script, given schema and prefix.'''
    return CREATE_SCRIPT.replace('{SCHEMA}', schema).replace('{PREFIX}', prefix)


class SqlExtractor(object):
    '''Class that deals with extracting various numeric data from a SQL table
    and storing the data in the sql afterwards.'''
    
    def __init__(self, **kwargs):
        self._user = unicode(kwargs.get('user'))
        self._passwd = unicode(kwargs.get('passwd', ''))
        self._host = unicode(kwargs.get('host', '127.0.0.1'))
        self._port = int(kwargs.get('port', 3306))
        self._db = unicode(kwargs.get('db'))
        self._prefix = unicode(kwargs.get('prefix', ''))
        self._intable = unicode(kwargs.get('intable', ''))
        
        self._conn = MySQLdb.connect(user=self._user,
                                     passwd=self._passwd,
                                     host=self._host,
                                     port=self._port,
                                     db=self._db,
                                     use_unicode=True,
                                     charset='utf8')
        self._extractor = NumExtractor()
        self._create_tables()
    
    def _create_tables(self):
        cur = self._conn.cursor()
        for command in sql_create_script(self._db, self._prefix).split(';'):
            if len(command.strip()) > 3:
                cur.execute(command)
    
    def _abs_prefix(self):
        return '`' + self._db + '`.`' + self._prefix
    
    def _abs_intable(self):
        return self._abs_prefix() + self._intable + '`'
    
    def _insert_rr(self, epiId, field, values):
        tuples = []
        for entry in values['record_bloodpressure']:
            systolic, diastolic, pulse = None, None, None
            if 'systolic' in entry:
                systolic = entry['systolic']['value']
            if 'diastolic' in entry:
                diastolic = entry['diastolic']['value']
            if 'pulse' in entry:
                pulse = entry['pulse']['value']
            tuples.append((epiId, field, systolic, diastolic, pulse))
        if len(tuples) > 0:
            cur = self._conn.cursor()
            cur.execute('begin')
            cur.executemany('insert into ' + self._abs_prefix() + 'rr` (epiId, field, systolic, diastolic, pulse) values (%s, %s, %s, %s, %s)', tuples)
            cur.execute('commit')
    
    def _insert_temp(self, epiId, field, values):
        tuples = []
        for entry in values['record_temperature']:
            temp = entry['temperature']['value']
            tuples.append((epiId, field, temp))
        if len(tuples) > 0:
            cur = self._conn.cursor()
            cur.execute('begin')
            cur.executemany('insert into ' + self._abs_prefix() + 'temp` (epiId, field, temp) values (%s, %s, %s)', tuples)
            cur.execute('commit')
    
    def _insert_kmi(self, epiId, field, values):
        pass
    
    def process(self, field):
        sql = 'SELECT `epiId`, `' + field + '` FROM ' + self._abs_intable()
        print sql
        cur = self._conn.cursor()
        cur.execute(sql)
        
        row = cur.fetchone()
        while row is not None:
            if row[1] is not None:
                epiId = long(row[0])
                document = unicode(row[1])
                values = self._extractor.extract(document)
                
                self._insert_rr(epiId, field, values)
                #self._insert_temp(epiId, field, values)
            row = cur.fetchone()

'''
CREATE TABLE `bloodpressures_split` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `splitId` bigint(11) NOT NULL,
  `systolic` int(5) DEFAULT NULL,
  `diastolic` int(5) DEFAULT NULL,
  `pulse` int(5) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `bloodpressures_split_id_idx` (`splitId`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_estonian_ci;
'''

class SqlVisitExtractor(object):
    '''Extractor for bloodpressure data in splitted epicrisis.'''
    
    def __init__(self, **kwargs):
        self._user = unicode(kwargs.get('user'))
        self._passwd = unicode(kwargs.get('passwd', ''))
        self._host = unicode(kwargs.get('host', '127.0.0.1'))
        self._port = int(kwargs.get('port', 3306))
        self._db = unicode(kwargs.get('db'))
        
        self._conn = MySQLdb.connect(user=self._user,
                                     passwd=self._passwd,
                                     host=self._host,
                                     port=self._port,
                                     db=self._db,
                                     use_unicode=True,
                                     charset='utf8')
        self._extractor = NumExtractor()

    def to_plain(self, json):
        sentences = ast.literal_eval(json)
        return u' '.join([word['sone'].decode('unicode_escape', 'replace') for sent in sentences for word in sent])

    def _insert_rr(self, row, values):
        visitId, epiId, epiTime, patId, epiType, fieldName, date, _ = row
        tuples = []
        for entry in values['record_bloodpressure']:
            systolic, diastolic, pulse = None, None, None
            if 'systolic' in entry:
                systolic = entry['systolic']['value']
            if 'diastolic' in entry:
                diastolic = entry['diastolic']['value']
            if 'pulse' in entry:
                pulse = entry['pulse']['value']
            tuples.append((visitId, epiId, epiTime, patId, epiType, fieldName, date, systolic, diastolic, pulse))
        if len(tuples) > 0:
            cur = self._conn.cursor()
            cur.execute('begin')
            cur.executemany('insert into `' + self._db + '`.`bloodpressures_visits` (visitID, epiId, epiTime, patId, epiType, fieldName, date, systolic, diastolic, pulse) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', tuples)
            cur.execute('commit')

    def process(self):
        sql = 'SELECT id, epiId, epiTime, patId, epiType, fieldName, date, json from `' + self._db + '`.`visits`;'
        print sql
        cur = self._conn.cursor()
        cur.execute(sql)
        
        row = cur.fetchone()
        while row is not None:
            if row[7] is not None:
                values = self._extractor.extract(self.to_plain(row[7]))
                self._insert_rr(row, values)
                #self._insert_temp(epiId, field, values)
            row = cur.fetchone()

if __name__ == '__main__':
    extr = SqlVisitExtractor(user='etsad', passwd='', host='127.0.0.1', port=3306, db='work')
    extr.process()
 
