"""Repeated Donor Analysis

This module processes a donations given in the FEC format and a percentile value.
It identifies repeated donors and computes the number of donations, the
total amount of donations and the percentile of donations from  repeated
to donors from a given zip code to a fixed recipient.


Example:
        $ python repeated_donor_analysis.py input_file output_file percentile

Attributes:
    repeat_donors (dict): stores a donor's (identified by name and zip-code)
        earliest year of donation. This allows determining whether a donation
        comes from a repeated donor in constant time
    recipients (dict): stores the $-amount of donations
        under the key (recipient, zip-code, year). The values are stored in a
        sorted list to allow for efficient percentile computations.

"""

import sys
import math
import datetime
import re
from sortedcontainers import SortedList

repeat_donors = {}
recipients = {}


def main():
    """ Extracts the system arguments and runs process_file
    
    The function reads three inputs from the command line:
    input file, output file and a file containing a single
    integer, the percentile value. It reads these and
    passes them on to the function process_file.
    
    Args:
    
    Returns:
    
    """
    if len(sys.argv) > 2:
        percentile_file = open(sys.argv[2], 'r')
        percentile = percentile_file.read()
        process_file(percentile, sys.argv[0], sys.argv[1])



def process_file(percentile, input_file_path, output_file_path):
    """ Given a percentile, an input and an output file, computes percentiles of donations

    The function reads the input file sequentually and saves repeated donors.
    If a line contains donation from a repeated donor, then for the recipients
    donations from repeated donors from this zip code, the percentile value is
    computed and the information is stored in the output_content strin.
    After having processed the input file, output_content is written into the
    output_file_path.
    
    Args:
        percentile (int): percentile value that is computed
        input_file_path (string): A string with the path to the input file
        output_file_path (string): A string with the path to the output file
    
    Return:
    
    """
    output_content = ''
    with open(input_file_path, 'r') as input_file:
        for line in input_file:
            entry = line.split('|')
            print(entry)
            if is_valid(entry):
                # extract relevant details of donation
                donation = extract(entry)
                # update donors information in repeat_donor
                add_donor(donation)
                # check if donation is from repeated donor, return recipient
                recipient_key = add_recipients(donation)
                if recipient_key is not None:
                    output_content += format_entry(percentile, recipient_key)
                    output_content += "\n"
        output_file = open(output_file_path, 'w+')
        output_file.write(output_content)
        output_file.close()


def format_entry(percentile, recipient_key):
    """ Given a percentile and (recipient,zip-code,year) key, returns the output string 

    The output string has the format:
    '|recipient|zip-code|year|percentile_value|total_amount|number of contributions'
    
    
    Args:
        percentile (int): percentile value that is computed
        recipient_key (tuple): A tuple of the form (recipient, zip-code, year),
            this is the key to the record we want to compute the percentile of.
    
    Return:
        line (string): a string summarizing the recipients donations
            from the zip code in the given year.
    
    """
    percentile_value, count = percentile_count(percentile, recipient_key)
    entry = recipients[recipient_key]
    amount = sum(entry)
    line = recipient_key[0] + '|' + recipient_key[1] + '|'
    line += str(recipient_key[2]) + '|'
    line += str(percentile_value) + '|' + str(amount) + '|'
    line += str(count)
    return line


def percentile_count(percentile, recipient_key):
    """ Given a percentile and (recipient,zip-code,year) key, returns the percentile and the count of the contributions

    It uses the recipient_key to access all donations to the recipient in the
    given year and zip-code. These donations are in the form of a sorted list,
    the percentile can be easily computed via the nearest rank method.
    The number of contributions is also computed and returned.
    
    Args:
        percentile (int): percentile value that is computed
        recipient_key (tuple): A tuple of the form (recipient, zip-code, year), this is the key
            to the record we want to compute the percentile of.
    
    Return:
        percentile value (int): Percentile value of contributions
        count (init): number of contributions
    
    """
    count = len(recipients[recipient_key])
    if percentile == 0:
        return recipients[recipient_key][0], count
    index = math.ceil(percentile / 100 * count) - 1
    return recipients[recipient_key][index], count


def extract(line):
    """ Given a line containing a valid donation, extracts the information we need.

    It extracts CMTE_ID, Name of donor, Zip-code, Year,
    and amount of donation in a list in this order
    
    Args:
        line (list): list containing the details of a valid donation
        from the original file
    
    Return:
        entry (list): Returns a list with the relevant details of the donation,
            it has the formation [CMTE_ID, Name, Zip-code, Year, Amount]
    
    """
    entry = []
    entry.append(line[0])             # CMTE_ID
    entry.append(line[7])             # Name
    entry.append(line[10][:5])        # Zip-code
    entry.append(int(line[13][-4:]))  # Year
    entry.append(int(line[14]))       # Amount
    return entry


def is_valid(entry):
    """ Checks if entry has valid format
    
    It checks whether the entry is an individual contribution,
    whether the date format is valid, whether the zip code
    or the name is malformed and also check the CMTE_ID and
    the Transaction_AMT are not empty
    
    Args:
        entry (list): list containing the details of the donation from the original
            file
    
    Return:
        boolean: True if entry is valid, False otherwise

    """
    # Check if Other_ID is empty
    if entry[15] != '':
        return False
    # Check if donation date is malformed
    is_zip = re.compile(r'\d{5}.*')
    try:
        datetime.datetime.strptime(entry[13], '%m%d%Y')
    except ValueError:
        return False
    # Check if zip code is malformed
    if is_zip.match(entry[10]) is None:
        return False
    # check if name is malformed
    if entry[7] == '' or len(entry[7].split(",")) < 2:
        return False
    # check if CMTE_ID, Transaction_AMT are non-empty
    if entry[0] == '' or entry[14] == '':
        return False
    return True


def add_donor(entry):
    """ If this is the donors earliest donation, then it saves the year of this donation under the donor's key

    Checks if donor (identified by name + zip code) has an earlier donation.
    If that is the case, it checks whether the new donation record is
    from an earlier time (our input may not be chronological). In this
    case, it updates the value to the year of the current entry.
    If this is the first donation, then the year is stored
    under the donor's key.
    
    Args:
        entry (list): list containing the details of the donation, it has
            the format_entry [recipient, donor name, zip, year, amount]
    
    Return:
        No return value
    
    """
    donor_key = entry[1] + entry[2]  # name+zip
    if donor_key in repeat_donors:
        if repeat_donors[donor_key] > entry[3]:
            repeat_donors[donor_key] = entry[3]
    else:
        repeat_donors[donor_key] = entry[3]


def add_recipients(entry):
    """ Checks if donation is from repeated donor and adds it to recipient list.

    If the entry is from a repeated donor, then the donation will be added to
    list of donations to the recipient from the zip code. Hence, the tuple
    (recipient, zip, year) is used as the key in the dictionary recipients.
    The value associated is a sorted list of the $-amount of the donations.
    The sorted list is used adding to it has amortized constant time complexity
    and a sorted list allows for fast percentile computation.
    
    Args:
        entry (list): list containing the details of the donation,
            it has the format_entry [recipient, donor name, zip, year, amount]
    
    Return:
        recip_key (tuple): None if donation was not from repeated donor.
            Otherwise the tuple (recipient, zip, year) which was
            used to save the amount
    
    """
    donor_key = entry[1] + entry[2]
    recip_key = None
    #  check if donor has donated in a previous year
    if donor_key in repeat_donors and repeat_donors[donor_key] < entry[3]:
        # store donation amount under (recipient, zip, year)
        recip_key = (entry[0], entry[2], entry[3])
        if recip_key in recipients:
            recipients[recip_key].add(entry[4])
        else:
            recipients[recip_key] = SortedList([entry[4]])
    return recip_key


# Only run main if module is executed as main
if __name__ == "__main__":
    main()
