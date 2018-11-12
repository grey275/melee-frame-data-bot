import gspread

from config import Config
from response import Response
import messages


class AllStructuredData(Response):
    """
    Stores all responses to user data in a tree structure,
    and a way to trigger those responses though a recursive
    fuzzy search.
    """
    sheet_url = Config.sheet_url
    character_names = Config.character_names

    def __init__(self, session):
        super().__init__()
        self._name = "Characters/Commands"
        self._children = self._build(session)

    def _build(self, session):
        get_worksheet = self._fetchAllWorksheets(session).worksheet
        children = dict()
        children.update(self._buildCharacters(get_worksheet),
                        **{"Help": Help()},
                        **{"Characters": Charlist()},
                        **{"Invite": Invite()},
                        **{"Info": Info()})
        return children

    def _buildCharacters(self, get_worksheet):
        characters = dict()
        for char in self.character_names:
            print("building {}".format(char))
            characters[char] = Character(get_worksheet(char))
        return characters

    def _fetchAllWorksheets(self, session):
        gc = gspread.Client(None, session)
        return gc.open_by_url(self.sheet_url)


class Help(Response):
    def __init__(self):
        super().__init__()
        self.output = messages.HELP


class Invite(Response):
    link = Config.invite_link

    def __init__(self):
        super().__init__()
        self.output = [{"content": self.link}]


class Info(Response):
    def __init__(self):
        super().__init__()
        self.output = messages.INFO


class Charlist(Response):
    chars = Config.character_names

    def __init__(self):
        super().__init__()
        msg = self._formatOutputList(self.chars)
        self.output.append({"content": msg})


class Worksheet(Response):
    """
    Base class for the data extracted from the sheets.
    """

    def __init__(self, worksheet):
        super().__init__()

        self._all_values = worksheet.get_all_values()
        # self.worksheet

    def _getRect(self, start_row, start_col, end_col=False):
        rect = list()
        if end_col is False:
            end_col = self._getRowSectLength(self._all_values[start_row],
                                             start_col)
        for row in self._all_values[start_row:]:
            sect_len = self._getRowSectLength(row, start_col)
            if sect_len < end_col:
                return rect
            rect.append(row[start_col:end_col])
        return rect

    def _getRowSectLength(self, row, start):
        for i in range(start, len(row)):
            if not row[i]:
                break
        return i

    def _getTableSection(self, start_row, col_range):
        """
        Gets a section of the table.
        Starts at the top of the table, and adds each row
        consecutively until a row is found with missing elements.
        """
        start_col, end_col = col_range
        section = list()
        row_len = len(self._all_values)
        for i in range(start_row, row_len):
            row = self._all_values[i][start_col:end_col]
            if not any(row):
                break
            section.append(row)
        # if self._name == "Fox":
        return section

    def _getSectionCols(self,  section):
        return [list(col) for col in zip(*section)]


class General(Worksheet):
    """
    Universal Framedata
    """
    def __init__(self, worksheet):
        super().__init__(worksheet)
        self.output.append({"embed": self._buildEmbed()})

    def _buildEmbed(self):
        self._name = title = "General"
        fields = self._addMoves() + self._addMisc()
        header = "These are the same for most characters"
        return self._makeEmbedOBJ(fields=fields, title=title, header=header)

    def _addMoves(self):
        labels, *moves = self._getRect(2, 0)
        fields = list()
        *most_labels, last_label = labels
        for name, *data in moves:
            *most_data, last_data = data
            most_value = "".join(("{}: {}, ".format(l, d)
                                  for l, d in zip(most_labels, last_label)))
            last_value = "{}: {}".format(last_label, last_data)

            fields.append({"name": name, "value": most_value+last_value})
        return fields

    def _addMisc(self):
        data = self._getRect(2, 5)
        fields = list()
        for name, value in data:
            fields.append({"name": name, "value": value})
        return fields


class Character(Worksheet):
    """
    Takes worksheet containing Character info and
    structures its data.
    """
    _name_loc = 0, 1

    def __init__(self, worksheet):
        super().__init__(worksheet)

        self._worksheet = worksheet
        self._name = self._findName()
        self._children = self._buildChildren()
        self.output = self._buildOutput()
        del self._all_values

    def _findName(self):
        name_row, name_col = self._name_loc
        return self._all_values[name_row][name_col]

    def _buildChildren(self):
        children = dict()
        moves = self._buildMoves()
        children.update(moves)
        return children

    def _buildMoves(self):
        start_row = 2
        start_col = 1
        labels, *move_table = self._getRect(start_row, start_col)
        # The first label is the 'Name' label, so we remove it.
        labels.pop(0)
        moves = dict()
        for row in move_table:
            move_name, *data = row
            moves[move_name] = Move(self._name, move_name,
                                    labels, data)
        return moves

    def _buildOutput(self):
        stat_table = self._buildStats()
        labeled_move_names = self._labelMoveNames()
        output = list()
        embeds = (self._embedStats(stat_table),
                  self._embedMoveList(labeled_move_names))

        for embed in embeds:
            output.append({"embed": embed})

        return output

    def _embedStats(self, stat_table):
        title = "{}'s General Stats".format(self._name)
        fields = list()
        for n, v in stat_table:
            breakpoint()
            fields.append({"name": n, "value": v})
        return self._makeEmbedOBJ(fields=fields, title=title)

    def _embedMoveList(self, labeled_move_names):
        title = "{}'s Moves".format(self._name)
        fields = list()
        for label, names in labeled_move_names.items():
            name_str = self._formatOutputList(names)
            fields.append({"name": label, "value": name_str})
        return self._makeEmbedOBJ(title=title, fields=fields)

    def _buildStats(self):
        start_row = 2
        start_col = self._worksheet.find("Jumpsquat Frames").col - 1
        end_col = start_col+2
        col_range = start_col, end_col
        stat_table = self._getTableSection(start_row, col_range)
        breakpoint()
        return stat_table

    def _labelMoveNames(self):
        move_list_range = 0, 2
        start_row = 3
        move_list_table = self._getTableSection(start_row, move_list_range)

        curr_label, name = move_list_table[0]
        labeled_names = {curr_label: [name]}
        for label, name in move_list_table[1:]:
            if label:
                curr_label = label
                labeled_names[curr_label] = [name]
            else:
                labeled_names[curr_label].append(name)
        return labeled_names


class Move(Response):
    def __init__(self, character, name, labels, data):
        super().__init__()
        self._name = name
        if labels[-1] == "Gif":
            data, url = data[:-1], data[-1]
            is_giffed = url is not "-" or not url
        else:
            is_giffed = False
        self.output.append({"embed": self._makeEmbed(character, labels, data)})
        if is_giffed:
            self.output.append({"content": url})
        else:
            self.output.append({"content": "No gif!"})

    def _makeEmbed(self, character, labels, data):
        title = "{}'s {}".format(character, self._name)
        fields = [{"name": l, "value": d} for l, d in zip(labels, data)]
        return self._makeEmbedOBJ(title=title, fields=fields)

