.. highlight:: none

Report
======

Introduction
------------

Architecture
------------

The architecture is split into three big parts. The first part is the scanning
and the OCR with ABBYY FineReader 9.0 Corporate Edition, the second part is the
parsing and the storing into a PostgreSQL database and the last part is the web
frontend for acessing the database.

First we scanned the printed pages of the 26 volumes of the Turkology Annual.
Then we used the Optical Character Recognition (OCR) software ABBYY FineReader
9.0 Corporate Edition to recoginze the scanned text. Therefore we used about 20
scanning languages. Unfortunately, there was no output format which presevered
all inforamtion which was gathered by the OCR software. So we used two different
output formats to process the scanning output further. The first output format
was WordML. This output format preserves hyphenation, formatting and the
languages. The second output format was PDF with the original image as overlay.
Thus we found out the page number and the exact position in the page of a piece
of text. This PDF was converted to plain text with a special patched version of
pdftotext which is a part of xpdf to preserve the position information.

For the next step we used the programming language Python 3. In this step we
aligned the converted text file and the WordML file. Then we parsed the
structure of the entries in the Turkology Annual with the help of LEPL 3, a
recursive decent parser for Python 3. We stored the parsing results in an
intermediate Python format. The access to the PostgreSQL database happened with
SQLAlchemy, a Python SQL Toolkit and Object Relational Mapper (ORM). From the
intermediate format we stored the parsed data into this database.

The webfront end is based on the web framework Django. As search engine we used
PyLucene which is based on Apache Lucene. So we was able to use the same Object
Relational Mapping as we used for the database access in the second step.

Difficulties
------------

Our approach based on hand-craftet rules and multi-level architecture was not 
successful with regard to a number of entries from the Turkology
Annual. Even though, we were controlling the precision of the developed rules
throughout the course of the project, and we tried to improve their performance,
we did not reach a point were all the records extracted from the scanned data
were correctly parsed. Particularly, introducing general patterns
resulted in the increase of false positive, whereas using more precise ones
leaded to the decrease of true positives and required the development of further
rules with ascending complexity. 

In the following, we present several examples of incomplete or incorrect parsing.
In order to keep our investigation organised we introduce several *ad-hoc*
groups corresponding to the reason for failed analysis. The presented examples
are assumed to be representative for the majority of incomplete records within
the database. We do not, however, aim to present a full topology of them, i.e.,
the introduced groups do not need to embrace all incorrect parses. For
convenience reasons, we will offer the correct interpretation and the record
from the database for every investigated case (cf. Appendix 1 in the full
documentation).

OCR Problems
^^^^^^^^^^^^

This section presents a handful examples of incorrect entries' parsing arising
from the inaccuracy of *optical character recognition*. Basically, the
multilanguage OCR used within the project does not yield many errors in the
recognition of word-like string sequences. Furthermore, such errors does not
have much influence on the parsing, so that the database's records are mostly
complete in such cases. Conversely, there were lots of mistakes regarding the
punctuation marks, which are of great importance to our rule-based paradigm.
Most of the entries containing such mistakes could be parsed only partially or
not at all. 

Conclusions
-----------

For the full documentation see this :download:`PDF file <../docs/documentation.pdf>`.

