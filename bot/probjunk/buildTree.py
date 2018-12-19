class Root(dict):
    '''
    Stores all responses to user data in a tree structure,
    and a way to trigger those responses though a recursive
    fuzzy search.
    '''
    conf = config.AllStructuredData

    def __init__(self, session):
        super().__init__('Commands', is_root=True)
        self.update(self._build(session))
        self._output.append(WrittenMSG('NoArgs').get())

    def _build(self, session):
        get_worksheet = self._fetchAllWorksheets(session).worksheet
        child_list = [
            WrittenResponse('Help', send_dm_default=True,
                            contrib_list=self.conf.contrib_list),
            ListResponse('Character Names', self.conf.char_names),
            WrittenResponse('Invite', link=self.conf.invite_link),
            WrittenResponse('Info', send_dm_default=True)
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
