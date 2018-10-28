import serviceAccount
import sheets

session = serviceAccount.createAssertionSession()
data = sheets.AllStructuredData(session)
"""TODO:
commands.discordClient.run()
"""
