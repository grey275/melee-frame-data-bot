import json

import gspread
import discord

from . import messages
from . import config
from . import logs


logger = logs.my_logger.getChild(__name__)


class Node(dict):
    def __init__(self, name):
        self.name = name
        self['output'] = list()
        self['aliases'] = list()
        self['children'] = dict()

    def _formatOutputList(self, lst):
        """
        formats a list of elements into a string to be
        displayed to the user directly.
        """
        *most, last = lst
        return "".join(["{}, ".format(c) for c in most] + [last])


class Root(Node):
    '''
    Stores all responses to user data in a tree structure,
    and a way to trigger those responses though a recursive
    fuzzy search.
    '''
    conf = config.Root

    def __init__(self, session):
        super().__init__("root")
        self["children"].update(self._build(session))
        self["output"].append(messages.WrittenMSG('NoArgs').get())

    def _build(self, session):
        get_worksheet = self._fetchAllWorksheets(session).worksheet
        child_list = [
            WrittenNode('Help', send_dm_default=True,
                        contrib_list=self.conf.contrib_list),
            # ListResponse('Character Names', self.conf.char_names),
            WrittenNode('Invite', link=self.conf.invite_link),
            WrittenNode('Info', send_dm_default=True),
        ]
        for char in self.conf.char_names:
            child = Character(char, get_worksheet(char))
            child_list.append(child)

        return {child.name: child for child in child_list}

    def _buildCharacters(self, get_worksheet):
        characters = dict()
        for char in self.conf.char_names:
            logger.debug('building {}'.format(char))
            characters[char] = Character('char', get_worksheet(char))
        return characters

    def _fetchAllWorksheets(self, session):
        gc = gspread.Client(None, session)
        return gc.open_by_url(self.conf.sheet_url)


class SuggestAlias(Node):
    def __init__(self):
        super().__init__('Suggest')


class WrittenNode(Node):
    def __init__(self, key, send_dm_default=False, **info):
        super().__init__(key)
        msg = messages.WrittenMSG(key, **info).get()
        self['output'].append(msg)


class Worksheet(Node):
    '''
    Base class for the data extracted from a sheet.
    '''

    def __init__(self, name, worksheet):
        super().__init__(name)

        self._all_values = worksheet.get_all_values()
        # self.worksheet

    def _getRect(self, start_row, start_col, end_col=False):
        '''
        Returns the largest rectangle with no completely
        empty cells specified by the arguments.
        '''
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
        '''
        Gets a section of the table.
        Starts at the top of the table, and adds each row
        consecutively until a row is found with missing elements.
        '''
        start_col, end_col = col_range
        section = list()
        row_len = len(self._all_values)
        for i in range(start_row, row_len):
            row = self._all_values[i][start_col:end_col]
            if not any(row):
                break
            section.append(row)
        return section

    def _getSectionCols(self,  section):
        return [list(col) for col in zip(*section)]



class General(Worksheet):
    '''
    Universal Framedata
    '''
    def __init__(self, worksheet):
        super().__init__('General', worksheet)
        self['ouput'].append({'embed': self._buildEmbed()})

    def _buildEmbed(self):
        title = 'General'
        header = 'These are the same for most characters'
        embed = discord.Embed(title=title, header=header)
        for field in self._addMoves() + self._addMisc():
            embed.add_field(**field)
        return embed

    def _addMoves(self):
        labels, *moves = self._getRect(2, 0)
        fields = list()
        *most_labels, last_label = labels
        for name, *data in moves:
            *most_data, last_data = data
            most_value = ''.join(('{}: {}, '.format(l, d)
                                  for l, d in zip(most_labels, last_label)))
            last_value = '{}: {}'.format(last_label, last_data)

            fields.append({'name': name, 'value': most_value+last_value})
        return fields

    def _addMisc(self):
        data = self._getRect(2, 5)
        fields = list()
        for name, value in data:
            fields.append({'name': name, 'value': value})
        return fields


class Character(Worksheet):
    '''
    Takes worksheet containing Character info and
    structures its data.
    '''

    def __init__(self, name, worksheet):
        super().__init__(name, worksheet)

        self._worksheet = worksheet
        self['children'] = self._buildMoves()
        logger.debug(f'Building {self.name}')
        self['output'] = self._buildOutput()
        del self._all_values

    def _buildMoves(self):
        start_row = 2
        start_col = 1
        labels, *move_table = self._getRect(start_row, start_col)
        # The first label is the 'Name' label, so we remove it.
        labels.pop(0)
        moves = dict()
        i = 0
        for row in move_table:
            move_name, *data = row
            moves[move_name] = Move(move_name, self.name,
                                    labels, data)
            i += 1
        return moves

    def _buildOutput(self):
        output = [
            {'embed': self._buildStats()},
            {'embed': self._buildMoveList()},
        ]

        return output

    def _buildStats(self):
        return self._structureStats(self._buildStatTable())

    def _buildStatTable(self):
        start_row = 2
        start_col = self._worksheet.find('Jumpsquat Frames').col - 1
        end_col = start_col+2
        col_range = start_col, end_col
        stat_table = self._getTableSection(start_row, col_range)
        return stat_table

    def _structureStats(self, stat_table):
        stats = dict()
        stats['title'] = '{}\'s General Stats'.format(self.name)
        stats['fields'] = list()
        for n, v in stat_table:
            stats['fields'].append({'name': n, 'value': v})
        return stats

    def _buildMoveList(self):
        return self._structureMoveList(self._labelMoveNames())

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

    def _structureMoveList(self, labeled_move_names):
        move_list = dict()
        move_list["title"] = '{}\'s Moves'.format(self.name)
        move_list['fields'] = list()
        for label, names in labeled_move_names.items():
            name_str = self._formatOutputList(names)
            move_list['fields'].append({'name': label, 'value': name_str})
        return move_list


class Move(Node):
    def __init__(self, name, character, labels, data):
        super().__init__(name)
        *data, url = data
        structured = self._structure(character, name, labels, data)
        self['output'].append({'embed': structured})
        self['output'].append({'content': url})

    def _structure(self, character, name, labels, data):
        struct = dict()
        struct['title'] = '{}\'s {}'.format(character, name)
        struct['fields'] = list()
        for l, d in zip(labels, data):
            struct['fields'].append({'name': l, 'value': d})
        return struct


if __name__ == "__main__":
    import serviceAccount
    data = Root(serviceAccount.createSession())

    with open(config.TREE_LOC, 'w') as f:
        f.write(json.dumps(data))
