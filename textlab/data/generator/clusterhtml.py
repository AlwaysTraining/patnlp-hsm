'''
Module for generating HTML that displays documents
with same label together.
'''

HTML_HEADER = '''<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8"/>
        <style>
        .cluster0 { background-color:hsl(0,100%,80%); }
        .cluster1 { background-color:hsl(49,100%,80%); }
        .cluster2 { background-color:hsl(98,100%,80%); }
        .cluster3 { background-color:hsl(147,100%,80%); }
        .cluster4 { background-color:hsl(196,100%,80%); }
        .cluster5 { background-color:hsl(245,100%,80%); }
        .cluster6 { background-color:hsl(294,100%,80%); }
        .cluster7 { background-color:hsl(343,100%,80%); }
        .cluster8 { background-color:hsl(32,100%,80%); }
        .cluster9 { background-color:hsl(81,100%,80%); }
        .cluster10 { background-color:hsl(130,100%,80%); }
        .cluster11 { background-color:hsl(179,100%,80%); }
        .cluster12 { background-color:hsl(228,100%,80%); }
        .cluster13 { background-color:hsl(277,100%,80%); }
        .cluster14 { background-color:hsl(326,100%,80%); }
        .cluster15 { background-color:hsl(15,100%,80%); }
        .cluster16 { background-color:hsl(64,100%,80%); }
        .cluster17 { background-color:hsl(113,100%,80%); }
        .cluster18 { background-color:hsl(162,100%,80%); }
        .cluster19 { background-color:hsl(211,100%,80%); }
        .cluster20 { background-color:hsl(260,100%,80%); }
        .cluster21 { background-color:hsl(309,100%,80%); }
        .cluster22 { background-color:hsl(358,100%,80%); }
        .cluster23 { background-color:hsl(47,100%,80%); }
        .cluster24 { background-color:hsl(96,100%,80%); }
        .cluster25 { background-color:hsl(145,100%,80%); }
        .cluster26 { background-color:hsl(194,100%,80%); }
        .cluster27 { background-color:hsl(243,100%,80%); }
        .cluster28 { background-color:hsl(292,100%,80%); }
        .cluster29 { background-color:hsl(341,100%,80%); }
        .cluster30 { background-color:hsl(30,100%,80%); }
        .cluster31 { background-color:hsl(79,100%,80%); }
        .cluster32 { background-color:hsl(128,100%,80%); }
        .cluster33 { background-color:hsl(177,100%,80%); }
        .cluster34 { background-color:hsl(226,100%,80%); }
        .cluster35 { background-color:hsl(275,100%,80%); }
        .cluster36 { background-color:hsl(324,100%,80%); }
        .cluster37 { background-color:hsl(13,100%,80%); }
        .cluster38 { background-color:hsl(62,100%,80%); }
        .cluster39 { background-color:hsl(111,100%,80%); }
        .cluster40 { background-color:hsl(160,100%,80%); }
        .cluster41 { background-color:hsl(209,100%,80%); }
        .cluster42 { background-color:hsl(258,100%,80%); }
        .cluster43 { background-color:hsl(307,100%,80%); }
        .cluster44 { background-color:hsl(356,100%,80%); }
        .cluster45 { background-color:hsl(45,100%,80%); }
        .cluster46 { background-color:hsl(94,100%,80%); }
        .cluster47 { background-color:hsl(143,100%,80%); }
        .cluster48 { background-color:hsl(192,100%,80%); }
        .cluster49 { background-color:hsl(241,100%,80%); }
        .cluster50 { background-color:hsl(290,100%,80%); }
        
        span {
            float:left;
            width:33%;
        }
        
        p {
            text-align:center;
        }

        </style>
    </head>
    <title>Documents and labels</title>
<body>
    <div>
'''

HTML_FOOTER = '''
    </div>
</body>
</html>'''

class ClusterHtml(object):
    
    @staticmethod
    def html(documents, labels):
        assert len(documents) == len(labels)
        
        buckets = {}
        for doc, lab in zip(documents, labels):
            bucket = buckets.get(lab, [])
            bucket.append(u'<p>' + doc + u'</p>')
            buckets[lab] = bucket
        
        html = HTML_HEADER
        for idx, label in enumerate(buckets):
            rows = [u'<p><b>{0} ({1} examples)</b></p>'.format(label, len(buckets[label]) + 1)] + list(sorted(buckets[label]))
            html += u'<span class="cluster{0}">{1}</span>'.format(idx, u'\n'.join(rows))
        html += HTML_FOOTER
        
        return html
