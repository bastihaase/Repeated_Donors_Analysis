import repeated_donor_analysis as ra
from sortedcontainers import SortedList
import unittest


class TestRepeatedDonorAnalysisMethods(unittest.TestCase):
    """
    This class tests the methods defined in repeated_donor_analysis.py
    
    For each of the helper methods, it initializes multiple scenarios of possible use cases.
    In particular, we test if the methods handle unclean data.
    The name of the functions follow the pattern test_method_name. We have named the variables
    within the function so that it is clear which scenario they are testing.
    For instance, in test_is_valid, we have the variable data_error which sets up a scenario
    where our function should return false as the date is malformed.

    """

    def test_is_valid(self):
        """ Checks if entries are correctly classfied as valid and invalid based on challenge description"""
        correct_entry = 'CMTE_ID|1|2|3|4|5|6|JEROME, CHRISTOPHER|8|9|30033|11|12|08232017|40||16|17|18|19|20'.split('|')
        other_id_error = 'CMTE_ID|1|2|3|4|5|6|JEROME, CHRISTOPHER|8|9|30033|11|12|08232017|40|otherid|16|17|18|19|20'.split('|')
        date_error = 'CMTE_ID|1|2|3|4|5|6|JEROME, CHRISTOPHER|8|9|30033|11|12|0823201a|40||16|17|18|19|20'.split('|')
        zip_error = 'CMTE_ID|1|2|3|4|5|6|JEROME, CHRISTOPHER|8|9|30abcsd|11|12|08232017|40||16|17|18|19|20'.split('|')
        name_error = 'CMTE_ID|1|2|3|4|5|6|CHRISTOPHER|8|9|30033|11|12|08232017|40||16|17|18|19|20'.split('|')
        cmte_error = '|1|2|3|4|5|6|JEROME, CHRISTOPHER|8|9|30033|11|12|08232017|40||16|17|18|19|20'.split('|')
        amt_error = 'CMTE_ID|1|2|3|4|5|6|JEROME, CHRISTOPHER|8|9|30033|11|12|08232017|||16|17|18|19|20'.split('|')
        length_error = [1, 2, 3, 4]
        self.assertTrue(ra.is_valid(correct_entry))
        self.assertFalse(ra.is_valid(other_id_error))
        self.assertFalse(ra.is_valid(date_error))
        self.assertFalse(ra.is_valid(zip_error))
        self.assertFalse(ra.is_valid(name_error))
        self.assertFalse(ra.is_valid(cmte_error))
        self.assertFalse(ra.is_valid(amt_error))
        self.assertFalse(ra.is_valid(length_error))
        
    def test_add_recipient(self):
        """ Checks if recipients are only added from repeated donors"""
        ra.repeat_donors = {'Haase, Bastian30033': 2017}
        ra.recipients = {}
        entry1 = ['test_rec', 'Wurst, Hans', '30034', 2017, 100]
        entry2 = ['test_rec', 'Haase, Bastian', '30033', 2018, 100]
        entry3 = ['test_rec', 'Haase, Bastian', '30033', 2017, 180]
        key = ra.add_recipients(entry1)
        self.assertEqual(key, None)
        self.assertEqual(ra.recipients, {})
        key = ra.add_recipients(entry2)
        self.assertEqual(key, ('test_rec', '30033', 2018))
        self.assertEqual(ra.recipients, {('test_rec', '30033', 2018): SortedList([100])})
        key = ra.add_recipients(entry3)
        self.assertEqual(key, None)

    def test_add_donor(self):
        """ Checks if donors are correctly added and update in repeat_donors"""
        ra.repeat_donors = {}
        entry1 = ['test_rec', 'Wurst, Hans', '30034', 2017, 100]
        entry2 = ['test_rec', 'Haase, Bastian', '30033', 2018, 100]
        entry3 = ['test_rec', 'Haase, Bastian', '30033', 2017, 180]
        ra.add_donor(entry1)
        self.assertEqual(ra.repeat_donors, {'Wurst, Hans30034': 2017})
        ra.add_donor(entry2)
        self.assertEqual(ra.repeat_donors, {'Wurst, Hans30034': 2017, 'Haase, Bastian30033': 2018})
        ra.add_donor(entry3)
        self.assertEqual(ra.repeat_donors, {'Wurst, Hans30034': 2017, 'Haase, Bastian30033': 2017})

    def test_extract(self):
        """ checks if extract method ectracts the correct information"""
        correct_entry = 'CMTE_ID|1|2|3|4|5|6|JEROME, CHRISTOPHER|8|9|30033|11|12|08232017|40||16|17|18|19|20'.split('|')
        entry = ra.extract(correct_entry)
        self.assertEqual(entry, ['CMTE_ID', 'JEROME, CHRISTOPHER', '30033', 2017, 40])

    def test_percentile_count(self):
        """ check if percentile_count computes percentiles in the right way,
        even when either the percentile or the recipient key are invalid
        """
        ra.recipients['test'] = SortedList([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        perc, count = ra.percentile_count(30, 'test')
        self.assertEqual(perc, 3)
        self.assertEqual(count, 10)
        perc, count = ra.percentile_count(0, 'test')
        self.assertEqual(perc, 1)
        perc, count = ra.percentile_count(3, 'error')
        self.assertEqual(count, -1)
        perc, count = ra.percentile_count(-10, 'test')
        self.assertEqual(count, -2)

    def test_format_entry(self):
        """ Checks if our output format works correctly"""
        ra.recipients = {('test', '30033', 2017): SortedList([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])}
        formatted = 'test|30033|2017|3|55|10'
        self.assertEqual(formatted, ra.format_entry(30, ('test', '30033', 2017)))


# Run all tests

suite = unittest.TestLoader().loadTestsFromTestCase(TestRepeatedDonorAnalysisMethods)
unittest.TextTestRunner(verbosity=2).run(suite)
