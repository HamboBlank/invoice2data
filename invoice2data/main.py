#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import shutil
from os.path import join
import pkg_resources
import invoice2data.pdftotext as pdftotext
from invoice2data.template import read_templates
from invoice2data.output import invoices_to_csv
import logging
from time import time

logger = logging.getLogger(__name__)

FILENAME = "{ref} {type} {acc} PROCESSED.pdf"

def extract_data(invoicefile, templates=None, debug=False):
    if templates is None:
        templates = read_templates(
            pkg_resources.resource_filename('invoice2data', 'templates'))
    
    extracted_str = pdftotext.to_text(invoicefile).decode('utf-8')

    charcount = len(extracted_str)
    logger.debug('number of char in pdf2text extract: %d', charcount)
    # Disable OCR for now.
    #if charcount < 40:
        #logger.info('Starting OCR')
        #extracted_str = image_to_text.to_text(invoicefile)
    logger.debug('START pdftotext result ===========================')
    logger.debug(extracted_str)
    logger.debug('END pdftotext result =============================')

    logger.debug('Testing {} template files'.format(len(templates)))
    for t in templates:
        optimized_str = t.prepare_input(extracted_str)

        if t.matches_input(optimized_str):
            return t.extract(optimized_str)

    logger.error('No template for %s', invoicefile)
    return False

def main():
    "Take folder or single file and analyze each."

    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('--debug', dest='debug', action='store_true',
                        help='Print debug information.')

    parser.add_argument('--copy', '-c', dest='copy',
                        help='Copy renamed PDFs to specified folder.')

    parser.add_argument('--template-folder', '-t', dest='template_folder',
                        default=pkg_resources.resource_filename('invoice2data', 'templates'),
                        help='Folder containing invoice templates in yml file. Required.')

    parser.add_argument('--output-folder', '-o', dest='output_folder', default='.',
                        help='Folder to place output csv file.')

    parser.add_argument('input_files', type=argparse.FileType('r'), nargs='+',
                        help='File or directory to analyze.')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    output = []
    templates = read_templates(args.template_folder)
    for f in args.input_files:
        res = extract_data(f.name, templates=templates)
        if res:
            logger.info(res)
            output.append(res)
            if args.copy:
                filename = FILENAME.format(
                    ref=res['invoice_number'],
                    type=res['transaction_type'],
                    acc=res['account'])
                shutil.copyfile(f.name, join(args.copy, filename))
    output_name = join(args.output_folder, 'invoices-output-{0}.csv'.format(time()))
    invoices_to_csv(output, output_name)

if __name__ == '__main__':
    main()

