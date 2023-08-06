# AGouTI - Annotation of Genomic and Transcriptomic Intervals

## Introduction
High-throughput sequencing techniques have become very popular in molecular biology research. In many cases, obtained results are described by positions corresponding to the transcript, gene, or genome. Usually, to infer the biological function of such regions, it is necessary to annotate these regions with overlapping known genomic features, such as genes, transcripts, exons, UTRs, CDSs, etc. AGouTI is a tool designed to annotate any genomic or transcriptomic coordinates using known genome annotation data in GTF or GFF files. 

#### Main features
1. AGouTI works with coordinates describing positions within the genome and within the transcripts,
2. Ability to assign intragenic regions from provided GTF/GFF annotation (UTRs, CDS, etc.) or de novo (5’ part, middle, 3’ part, whole), 
3. Annotation of intervals in standard BED or custom column-based text files (TSV, CSV, etc.) in any non-standard format,  
4. Flexible handling of multiple annotations for a single region, 
5. Flexible selection of GTF/GFF attributes to include in the annotation. 

### Documentation

Full documentation is available at https://github.com/zywicki-lab/agouti

### Contribute

If you notice any errors and mistakes or would like to suggest some new features, please use Github's issue tracking system to report them. You are also welcome to send a pull request with your corrections and suggestions.

### License

This project is licensed under the GNU General Public License v3.0 license terms.

Anytree (Copyright (c) 2016 c0fec0de) and gffutils (Copyright (c) 2013 Ryan Dale) packages are distributed with this software to ensure full compatibility. Documentation, authors, license and additional information can be found at https://anytree.readthedocs.io/en/latest/ and https://github.com/daler/gffutils.
