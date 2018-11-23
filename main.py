import serviceAccount

import sheets
import client



session = serviceAccount.createSession()
data = sheets.AllStructuredData(session)
client = client.Client(data)

client.run()
