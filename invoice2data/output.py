# -*- coding: utf-8 -*-
import csv


def invoices_to_csv(data, path):
    with open(path, "w") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')

        writer.writerow(['Type', 'Account Reference', 'Nominal A/C Ref', 'Reference', 'Date', 'Tax Amount', 'Tax Code', 'Net Amount'])
        for line in data:
            writer.writerow([
                line['transaction_type'],
                line['account'],
                line['nom_ac_reference'],
                line['invoice_number'],
                line['date'].strftime('%d%m%Y'),
                line['amount_net_tax'],
                line['tax_code'],
                round(line['amount'] - line['amount_net_tax'], 2)
            ])

