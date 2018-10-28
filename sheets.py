from dataclasses import dataclass
from collections import namedtuple

import tablib

import gspread

from config import conf
import serviceAccount


credentials_filename = "./google-service-account.json"
name = "Copy of SSBM General Frame Data [WIP]"
key = "11i-YwUajgc6aWD8wSetYrb_bAM4RmL4FZi8XdBrMHo8"




@dataclass
class ValueRange(list):
    """
    Builds a range of values from 'data', defined by
    'start' and 'end'. The range is built from top to
    bottom, and if any rows have values missing the
    construction is cut short.
    """

    def __init__(self, coords, data):

        self[:] = self._findRect(coords.start, coords.end)


@dataclass
class RectCoords:
    row_start: int
    col_start: int

    row_end: int
    col_end: int

    Point = namedtuple("Point", ["row", "col"])

    def __post_init__(self):
        self.start = self.Point(self.row_start, self.col_start)
        self.end = self.Point(self.row_end, self.col_end)
        self.col_range = self.Point(self.col_start, self.col_end)
        self.row_range = self.Point(self.row_start, self.row_end)


class Sheet:
    """
    Base class for the data extracted from the sheets.
    """

    def __init__(self, worksheet):
        self._all_values = worksheet.get_all_values()

    def _nameData(self, starting_row, *col_range):
        """
        Store a table as a list, with the leftmost element
        of each row being a name.
        """
        sheet_name = self._all_values[0][1]
        print(" sheet_name: {} \n starting_row: {}\n col_range: {}\n".format(sheet_name,
                                                                           starting_row,
                                                                           col_range))
        named = dict()
        for row in self._all_values[starting_row:]:
            row = row[col_range[0]:col_range[1]]
            if not all(row):
                print("incomplete row:\n {}\n".format(row))
                return named
            name, *data = row
            named[name] = data

        return named


class Character(Sheet):
    """
    Takes worksheet containing Character info and
    structures its data.
    """

    def __init__(self, worksheet):
        super().__init__(worksheet)
        self._buildDataCategories()
        del self._all_values

    def _buildDataCategories(self):
        print("Building moves")
        self.moves = self._nameData(3, 1, 11)
        self.move_data_names = self._buildMoveDataNames()
        print("building attrs")
        self.char_attrs = self._nameData(3, 12, 14)

    def _buildMoveDataNames(self):
        return self._all_values[2][2:11]


class AllStructuredData:
    def __init__(self, service_account_session,
                 char_names=conf.character_names,
                 sheet_id=conf.sheet_id):

        self.session = service_account_session
        self.all_worksheets = self._getAllWorksheets(sheet_id)
        self.characters = self._buildCharacters(char_names)

    def _buildCharacters(self, char_names):

        characters = dict()
        for char in char_names:
            characters[char] = Character(self.all_worksheets.worksheet(char))

        return characters

    def _getAllWorksheets(self, sheet_id):
        gc = gspread.Client(None, self.session)
        return gc.open_by_key(sheet_id)
