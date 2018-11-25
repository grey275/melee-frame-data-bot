import logging

import gspread
import discord

import config

from messages import WrittenMSG
from response import Response, WrittenResponse, ListResponse
from searchableTree import SearchableTree

logger = logging.getLogger(__name__)
logger.propagate = True


class AllStructuredData(SearchableTree):
    '''
    Stores all responses to user data in a tree structure,
    and a way to trigger those responses though a recursive
    fuzzy search.
    '''
    conf = config.AllStructuredData

    def __init__(self, session):
        super().__init__('Commands')
        self._children = self._build(session)
        self._output.append(WrittenMSG('NoArgs').get())

    def _build(self, session):
        get_worksheet = self._fetchAllWorksheets(session).worksheet
        child_list = [
            WrittenResponse('Help', dm=True, contrib_list=self.conf.contrib_list),
            ListResponse('Character Names', self.conf.char_names),
            WrittenResponse('Invite', link=self.conf.invite_link),
            WrittenResponse('Info', dm=True),
            *(Character(char, get_worksheet(char)) for char in self.conf.char_names),
        ]

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


class Worksheet(SearchableTree):
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
        self._output.append({'embed': self._buildEmbed()})

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
        self._children = self._buildMoves()
        logger.debug(f'Building {self.name}')
        self._output = self._buildOutput()
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
        stat_table = self._buildStats()
        labeled_move_names = self._labelMoveNames()
        embeds = (self._embedStats(stat_table),
                  self._embedMoveList(labeled_move_names))

        return [{'embed': e} for e in embeds]

    def _embedStats(self, stat_table):
        title = '{}\'s General Stats'.format(self.name)
        embed = discord.Embed(title=title)
        for n, v in stat_table:
            embed.add_field(name=n, value=v)
        return embed

    def _embedMoveList(self, labeled_move_names):
        title = '{}\'s Moves'.format(self.name)
        embed = discord.Embed(title=title)
        for label, names in labeled_move_names.items():
            name_str = self._formatOutputList(names)
            embed.add_field(name=label, value=name_str)
        return embed

    def _buildStats(self):
        start_row = 2
        start_col = self._worksheet.find('Jumpsquat Frames').col - 1
        end_col = start_col+2
        col_range = start_col, end_col
        stat_table = self._getTableSection(start_row, col_range)
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
    def __init__(self, name, character, labels, data):
        super().__init__(name)
        self._output = self._makeMove(character, name, labels, data)

    def _makeMove(self, character, name, labels, data):
        output = list()
        *data, url = data
        output.append({'embed': self._makeEmbed(character, name, labels, data)})
        output.append({'content': url})
        return output

    def _makeEmbed(self, character, name, labels, data):
        title = '{}\'s {}'.format(character, name)
        embed = discord.Embed(title=title)
        for l, d in zip(labels, data):
            embed.add_field(name=l, value=d)
        return embed
