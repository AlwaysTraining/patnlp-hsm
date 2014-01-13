# -*- coding: utf-8 -*-
# Python 2.7
'''
Module for extracting blood pressures and other numeric values from
plain texts.
'''

try:
    import pyre2 as re
except ImportError:
    try:
        import regex as re
    except ImportError:
        import re

import sys
import codecs
# Generic functions for working with custom matchobjects

def dict_from_matchobject(matchobject):
    '''Convert a Python matchobject to custom dictionary.'''
    fields = matchobject.groupdict()
    d = dict()
    for field, value in zip(fields.keys(), fields.values()):
        d[field] = {
            'value':    value,
            'original': matchobject.group(field),
            'start':    matchobject.start(field),
            'end':      matchobject.end(field)}
    d['start']    = matchobject.start(0)
    d['end']      = matchobject.end(0)
    d['original'] = matchobject.group(0)
    return d

def cast_fields(d, fields, cast=int):
    '''Cast values of given fields in d to specified function'''
    for field in fields:
        if field in d:
            if cast == float:
                value = str(d[field]['value']).strip()
                value = re.sub('\s', '', value)
                value = re.sub(r'[.,]+', '.', value)
                d[field]['value'] = value
            try:
                d[field]['value'] = cast(d[field]['value'])
            except ValueError:
                sys.stderr.write(str(d))
                raise
    return d

def avg_estimates(d, fields, low_fields, high_fields):
    '''Compute average estimates for given fields.'''
    assert (len(fields) == len(low_fields))
    assert (len(low_fields) == len(high_fields))
    for field, low_field, high_field in zip(fields, low_fields, high_fields):
        if low_field not in d or high_field not in d:
            continue
        estimate = (d[low_field]['value'] + d[high_field]['value']) / 2 
        d[field] = {'value': estimate}
    return d

def correct_low_high(d, low_fields, high_fields):
    assert (len(low_fields) == len(high_fields))
    for low, high in zip(low_fields, high_fields):
        if low in d and high in d and d[low]['value'] > d[high]['value']:
            d[low], d[high] = d[high], d[low]
    return d

def in_range(d, fields, low_dict, high_dict):
    '''Check if all fields in d are in specified ranges.'''
    for field in fields:
        if field not in d:
            continue
        value = d[field]['value']
        if value < low_dict[field] or value > high_dict[field]:
            return False
    return True

def remove_submatches(ds):
    '''Remove matches that are submatches by some other match.'''
    n = len(ds)
    ok = [True]*n
    for i in range(n):
        A = ds[i]
        for j in range(i+1, n):
            B = ds[j]
            if A['start'] == B['start'] and A['end'] == B['end']:
                if len(A) > len(B):
                    ok[j] = False
                    continue
                elif len(A) < len(B):
                    ok[i] = False
                    continue
            if A['start'] >= B['start'] and A['end'] <= B['end']:
                ok[i] = False
            elif A['start'] <= B['start'] and A['end'] >= B['end']:
                ok[j] = False
    return [ds[i] for i in range(n) if ok[i]]

def get_matches(document, patterns):
    '''Match all specified patterns on given documents.'''
    f = dict_from_matchobject
    return [f(m) for p in patterns for m in p.finditer(document)]


class BloodPressure(object):
    '''Class for extracting blood pressures from plain text.'''

    fields      = ['systolic', 'diastolic', 'pulse']
    low_fields  = ['systolic_low', 'diastolic_low', 'pulse_low']
    high_fields = ['systolic_high', 'diastolic_high', 'pulse_high']
    all_fields  = fields + low_fields + high_fields
    
    # define acceptable ranges for blood pressure and pulse values
    # source:
    # http://www.vaughns-1-pagers.com/medicine/blood-pressure.htm
    # http://en.wikipedia.org/wiki/Pulse
    low_values  = {'systolic': 50,
                   'diastolic': 35,
                   'pulse': 20}
    high_values = {'systolic': 250,
                   'diastolic': 150,
                   'pulse': 200}
    
    def __init__(self, **kwargs):
        '''Initialize a new BloodPressure extractor.'''
        # define common regular expressions
        space = '\s*'
        dig = '[0-9]{2,3}'
        sep = space + '[/&-]' + space
        # define regular expressions for extracting blood pressure
        patterns = []
        
        # pattern, where low and high systolic / diastolic values are given
        # as two measurements
        patterns.append((
            '(?P<systolic_low>{0})\s*/\s*(?P<diastolic_low>{0})\s*/\s*'
            '(?P<systolic_high>{0})\s*/\s*(?P<diastolic_high>{0})').format(dig))
        # pattern, where blood pressure ranges are given with '-' character
        # and separated with /
        patterns.append((
            '(?P<systolic_low>{0})\s*-\s*(?P<systolic_high>{0}){1}'
            '(?P<diastolic_low>{0}){1}(?P<diastolic_high>{0})').format(dig, sep))
        # pattern, where blood pressure ranges are given with '/' character
        # and separated with -
        patterns.append((
            '(?P<systolic_low>{0})\s*/\s*(?P<diastolic_low>{0})\s*-\s*'
            '(?P<systolic_high>{0})\s*/\s*(?P<diastolic_high>{0})').format(dig))
            
        # pattern for blood pressures, where systolic is given as range
        patterns.append((
            '(?P<systolic_low>{0})\s*-\s*(?P<systolic_high>{0}){1}'
            '(?P<diastolic>{0})').format(dig, sep))

        # generic pattern for matching blood pressures
        patterns.append(
            '(?P<systolic>{0}){1}(?P<diastolic>{0})'.format(dig, sep))

        # more specific patterns, but allows more separators
        patterns.append(
            '[rR][rR]\D{0,3}?' + 
            '(?P<systolic>{0})\s*.\s*(?P<diastolic>{0})'.format(dig))
        # only for systolic
        patterns.append(
            '[rR][rR]\D{0,3}?' + 
            '(?P<systolic>{0})'.format(dig))
        
        # regular expression for extracting pulse
        pulse_single = '(?P<pulse>' + dig + ')(x(min)?)?'
        pulse_range  = '(?P<pulse_low>' + dig + ')' + sep + '(?P<pulse_high>' + dig + ')(x(min)?)?'
        pulse_prefix = u'((^)|([^a-zA-Z]))(ps|pulss|fr|p(?![üa-zA-Z])).{0,5}?'
        pulse_suffix = '(?!\s*(cm|mg|kg|l|ml|g))'
        pulse_dist   = '(.{0,35}?)'
        pulses = []
        pulses.append('(' + pulse_prefix + pulse_single + pulse_suffix + pulse_dist + ')')
        pulses.append('(' + pulse_prefix + pulse_range + pulse_suffix + pulse_dist + ')')
        pulses.append('(' + pulse_dist + pulse_prefix + pulse_single + pulse_suffix + ')')
        pulses.append('(' + pulse_dist + pulse_prefix + pulse_range + pulse_suffix + ')')
        
        # create regular expressions for matching optional pulse
        self.patterns = []
        for p in patterns:
            for pulse in pulses:
                self.patterns.append(re.compile(pulse + p, re.UNICODE))
                self.patterns.append(re.compile(p + pulse, re.UNICODE))
            self.patterns.append(re.compile(p, re.UNICODE))
        # patterns for only pulse and pulse ranges
        self.patterns.append(re.compile(pulse_prefix + pulse_single + pulse_suffix, re.UNICODE))
        self.patterns.append(re.compile(pulse_prefix + pulse_range + pulse_suffix, re.UNICODE))

    def extract(self, document):
        '''Given a document, return a list of dictionaries containing
           details about each measurement.           
           '''
        ms = get_matches(document, self.patterns)
        ms = [cast_fields(m, BloodPressure.all_fields, int) for m in ms]
        ms = [correct_low_high(m,
                               BloodPressure.low_fields,
                               BloodPressure.high_fields)
                               for m in ms]
        ms = [avg_estimates(m, 
                            BloodPressure.fields, 
                            BloodPressure.low_fields, 
                            BloodPressure.high_fields) 
                            for m in ms]
        # systolic value should be larger than diastolic, so check it
        def f(m):
            if 'systolic' in m and 'diastolic' in m:
                return m['systolic']['value'] > m['diastolic']['value']
            return True
        ms = [m for m in ms if f(m)]
        
        ms = [m for m in ms if in_range(m, BloodPressure.fields,
                                           BloodPressure.low_values, 
                                           BloodPressure.high_values)]
        return remove_submatches(ms)


class Temperature(object):
    '''Class for extracting temperatures from plain text documents.'''

    fields      = ['temperature']
    low_fields  = ['temperature_low']
    high_fields = ['temperature_high']
    all_fields  = fields + low_fields + high_fields
    
    # define acceptable ranges for blood pressure and pulse values
    # source:
    # http://www.vaughns-1-pagers.com/medicine/blood-pressure.htm
    # http://en.wikipedia.org/wiki/Pulse
    low_values  = {'temperature': 15}
    high_values = {'temperature': 50}
    
    def __init__(self, **kwargs):
        keywords  = '((^)|([^a-zA-Z]))((pal)|(t0)|(palavik(uga)?)|(t((emp)(eratuur)?)?))'
        digits    = '[1-9][0-9]([ ,.]*[0-9]{1,2})?(?![0-9])'
        guard     = '(?!\s*(mg)|(x)|(cm)|(mm)|(g)|(kg))'
        temp      = '(?P<temperature>' + digits + ')'
        temp_low  = '(?P<temperature_low>' + digits + ')'
        temp_high = '(?P<temperature_high>' + digits + ')'
        sep       = '[ .*-/](\D{0,35}?)'
        self.patterns = [
            re.compile(keywords + temp + guard, re.UNICODE),
            re.compile(keywords + sep + temp + guard, re.UNICODE),
            re.compile(keywords + temp_low + '\s*-\s*' + temp_high + guard, re.UNICODE),
            re.compile(keywords + sep + temp_low + '\s*-\s*' + temp_high + guard, re.UNICODE)
            ]
    
    def extract(self, document):
        ms = get_matches(document, self.patterns)
        ms = [cast_fields(m, Temperature.all_fields, float) for m in ms]
        ms = [correct_low_high(m,
                               Temperature.low_fields,
                               Temperature.high_fields)
                               for m in ms]
        ms = [avg_estimates(m, 
                            Temperature.fields, 
                            Temperature.low_fields, 
                            Temperature.high_fields) 
                            for m in ms]
        ms = [m for m in ms if in_range(m, Temperature.fields,
                                           Temperature.low_values, 
                                           Temperature.high_values)]
        return remove_submatches(ms)


class Medicine(object):

    def __init__(self, **kwargs):
        dig       = '[0-9]+([ .,]*[0-9]*)?'
        units     = '(?P<unit>(mg)|(g)|(tbl)|(d)|(ugx))'
        medicine  = '(?P<medicine>\\b[a-zA-Z]{3,50}\\b)[ .-]*((ravi|ret).{0,3}?)?'
        amount    = '(?P<amount>' + dig + ')\s*'
        frequency = '\s*[x*]\s*(?P<frequency>\d+)'
        n         = '\s*n\s*[.*]?\s*(?P<n>\d+)'
        
        self.patterns = [
            re.compile(medicine + amount + units, re.UNICODE),
            re.compile(medicine + amount + units + frequency, re.UNICODE),
            re.compile(medicine + amount + units + n, re.UNICODE),
            re.compile(medicine + amount + units + frequency + n, re.UNICODE),
            re.compile(medicine + amount + frequency, re.UNICODE),
            re.compile(medicine + amount + n, re.UNICODE)
            ]

    def extract(self, document):
        ms = get_matches(document, self.patterns)
        ms = [cast_fields(m, ['amount'], float) for m in ms]
        ms = [cast_fields(m, ['frequency', 'n'], int) for m in ms]
        return remove_submatches(ms)


class Date(object):

    months = [u'ja', u've', u'mä', u'ap', u'ma', u'juun', u'juul', u'aug', u'se', u'ok', u'no', u'de']
    
    def __init__(self, **kwargs):
        dig = '[0-9]{2,4}'
        month = u'jaanuar|veebruar|märts|aprill|mai|juuni|juuli|august|september|oktoober|november|detsember'
        month += u'|jaan|veeb|mär|apr|juun|juul|aug|sep|okt|nov|det'
        sep = '(\s*[./-]\s*| )'
        self.patterns = []
        self.patterns.append('(?P<day>' + dig +')' + sep + '(?P<month>' + month + '|' + dig + ').{0,2}?' + sep + '(?P<year>' + dig +')(?!' + sep + dig + sep + ')')
        self.patterns.append('(?P<day>' + dig +')' + sep + '(?P<month>' + month + '|' + dig + ').{0,2}?')
        self.patterns = [re.compile(p) for p in self.patterns]

    def _fix_month(self, month):
        for idx, mo in enumerate(Date.months):
            if month.startswith(mo):
                return idx+1
        return int(month)

    def _valid(self, mo):
        day = mo['day']['value']
        month = mo['month']['value']
        year = None
        if 'year' in mo:
            year = mo['year']['value'] # some clumsy year extension
            if year < 1000 and year < 80:
                year += 2000
            elif year < 1000 and year >= 80:
                year += 1900
            mo['year']['value'] = year
        v = day >= 1 and day <= 31 and month >= 1 and month <= 12
        if year != None:
            #sys.stderr.write('{0} {1} {2} {3}\n'.format(day,month,year,v))
            return v and year >= 1990 and year <= 2015
        #sys.stderr.write('{0} {1} {2} {3}\n'.format(day,month,year,v))
        return v
               
    def extract(self, document):
        ms = get_matches(document, self.patterns)
        for mo in ms:
            if 'month' in mo:
                mo['month']['value'] = self._fix_month(mo['month']['value'])
        ms = [cast_fields(m, ['day', 'year'], int) for m in ms]
        ms = [m for m in ms if self._valid(m)]
        return remove_submatches(ms)

class Timex(object):

    def __init__(self, **kwargs):
        dig = '[0-9]+\s*([,.]\s*[0-9]+)?'
        sep = '\s*[.x,/-]?\s*'
        times = u'(näd|kuu|päe|aast)\S*'
        
        patterns = []
        patterns.append(u'(?P<value>' + dig + ')' + sep + '(?P<expression>' + times + u')')
        self.patterns = [re.compile(p, re.UNICODE) for p in patterns]

    def extract(self, document):
        ms = get_matches(document, self.patterns)
        ms = [cast_fields(m, ['value'], float) for m in ms]
        ms = [m for m in ms if in_range(m, ['value'],
                                           {'value': 0.001}, 
                                           {'value': 9999}) ]
        return remove_submatches(ms)


class Measurements(object):
    
    def __init__(self, **kwargs):
        dig = '[0-9]+\s*[,.]?\s*[0-9]+'
        sep = '\s*[.,/-]?\s*'
        patterns = []
        patterns.append('(sp|kasv|pikk(us)?)' + sep + '(?P<height>' + dig + ')' + sep + '(cm|m)?')
        patterns.append(u'(pü|pea(ü)?.{0,9})' + sep + '(?P<head_diameter>' + dig + ')' + sep + '(cm)?')
        patterns.append('(sk|kaal)' + sep + '(?P<weight>' + dig + ')' + sep + '(k?g)?')
        
        self.patterns = [re.compile(p) for p in patterns]

    def extract(self, document):
        ms = get_matches(document, self.patterns)
        #sys.stderr.write(str(ms) + '\n')
        ms = [cast_fields(m, ['height', 'weight', 'head_diameter'], float) for m in ms]
        return remove_submatches(ms)


class NumExtractor(object):

    ignore = ['start', 'end', 'original']

    def __init__(self, **kwargs):
        self.extractors = {
            'record_bloodpressure': BloodPressure(**kwargs),
            'record_date': Date(**kwargs),
            'record_measurement': Measurements(**kwargs),
            'record_medicine': Medicine(**kwargs),
            'record_timex': Timex(**kwargs),
            'record_temperature': Temperature(**kwargs)}

    def extract(self, document):
        values = dict()
        for key in self.extractors:
            values[key] = self.extractors[key].extract(document)
        return values
    
    def _annots(self, title, m):
        annots = []
        for field in m:
            if field in NumExtractor.ignore or 'start' not in m[field]:
                continue
            s = u'<span class="{0}" title="{0} = {1}">'
            if isinstance(m[field]['value'], int) or isinstance(m[field]['value'], float):
                s = u'<span class="num {0}" title="{0} = {1}">'
            s = s.format(field, m[field]['value'])
            start, end = m[field]['start'], m[field]['end']
            annots.append((end - 0.1,   end, '</span>'))
            annots.append((start + 0.1, start, s))
        annots.append((m['end'], m['end'], '</span>'))
        annots.append((m['start'], m['start'], 
            '<span class="{0}" title="{0}">'.format(title)))
        return annots
    
    def annotate(self, document):
        values = self.extract(document)
        usable = [values[title] for title in values]
        usable = reduce(lambda x, y: x + y, usable)
        usable = remove_submatches(usable)
        annots = []
        for title in values:
            ms = values[title]
            for m in ms:
                annots.extend(self._annots(title, m))
        # generate annotated string
        annots.sort(key=lambda x: x[0], reverse=True)
        annotated = list(document)
        for _, idx, annot in annots:
            annotated[idx:idx] = annot
        return u''.join(annotated)

################################################################################
# functions for creating database tables
################################################################################

def create_bp_table(conn, data, tbl_name = 'tm_misplus_rr'):
    '''Create a SQLite table containing bloodpressures.
    conn - connection to SQLite3 database
    data - enumerable of tuples (vidx, text), where
        vidx - id of the text (used as foreign key in resulting table)
        text - free-text to match.
    tbl_name - specify the table name (NB! function will drop the old table,
               if it exists).'''
    cur = conn.cursor()
    # create the appropriate table
    cur.execute('drop table if exists ' + tbl_name)
    cur.execute('''create table if not exists ''' + tbl_name + '''(
                    id int(10) primary key,
                    vid int(10) not null,
                    systolic int,
                    diastolic int,
                    pulse int)''')
    # parse bloodpressures and prepare for batch insert
    pid = 1L
    ne = NumExtractor()
    bloodpressures = []
    for vid, text in data:
        values = ne.extract(text)
        for bp in values['record_bloodpressure']:
            t = (pid, vid,
                bp.get('systolic', dict()).get('value', None),
                bp.get('diastolic', dict()).get('value', None),
                bp.get('pulse', dict()).get('value', None))
            bloodpressures.append(t)
            pid += 1
    # insert data
    cur.executemany('insert into ' + tbl_name + '(id, vid, systolic, diastolic, pulse) values(?, ?, ?, ?, ?)', bloodpressures)
    # create indices
    cur.execute('create index rr_vid_idx on ' + tbl_name + '(vid)')
    cur.execute('create index rr_systolic_idx on ' + tbl_name + '(systolic)')
    cur.execute('create index rr_diastolic_idx on ' + tbl_name + '(diastolic)')
    cur.execute('create index rr_pulse_idx on ' + tbl_name + '(pulse)')

################################################################################
# deal with running the script directly from command line
################################################################################

_html_header = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/>
<style>
.record_temperature {
    background-color:lightgreen;
}
.record_bloodpressure {
    background-color:yellow;
}
.record_medicine {
    background-color:lightblue;
}
.record_date {
    background-color:purple;
}
.record_measurement {
    background-color:orange;
}
.record_timex {
    background-color:gray;
}
.num {
    font-weight:bold;
}
</style>
</head>
<body>
"""

_html_footer = """</body></html>"""

def main():
    extractor = NumExtractor()
    reader = codecs.getreader('utf-8')(sys.stdin)
    writer = codecs.getwriter('utf-8')(sys.stdout)
    writer.write(_html_header)
    line = reader.readline()
    while line != '':
        writer.write('<p>' + extractor.annotate(line) + '</p>')
        line = reader.readline()
    writer.write(_html_footer)


if __name__ == '__main__':
    main()
    '''reader = codecs.getreader('utf-8')(sys.stdin)
    lines = reader.readlines()
    lines = [(i+1, l) for i, l in enumerate(lines)]
    import sqlite3
    conn  = sqlite3.connect("test.sqlite3")
    create_bp_table(conn, lines)'''

