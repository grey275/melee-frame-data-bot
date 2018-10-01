import re
from math import floor

from main import Config, Sheets
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

class api:
    scope = "https://www.googleapis.com/auth/spreadsheets"
    store = file.Storage("token.json")
    creds = store.get()

    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', scope)
        creds = tools.run_flow(flow, store)

    service = build('sheets', 'v4', http=creds.authorize(Http()))
    conf = Config()
    sheets = Sheets(conf.spreadsheet_ID, conf.google_API_key)
    sheet_id = conf.sheet_id
    sheet_names = sheets.sheet_names
    value_request = service.spreadsheets().values()

def getDamage():
    ranges = ["{}!G4:G".format(sheet) for sheet in api.sheet_names]
    request = api.value_request.batchGet(spreadsheetId=api.sheet_id,
                                                      ranges=ranges)

    valueRanges = request.execute().get("valueRanges")
    return [v["values"] for v in valueRanges[:-3]]


def calculateShieldHitlag(damage_range):
    regex_single_hit = "^\d+$"
    regex_single_hit_diff = "\d+\/+\d+"
    regex_multihit_same = "^\d+\s\(\d+\*\d+\)$"
    regex_multihit_diff = "^\d+\s\(\d+(\+\d+)*\+\d+\)$"
    shield_hitlag_range = []
    for damage_str in damage_range:
        if damage_str == "-":
            shield_hitlag_range.append(damage_str)

        elif re.match(regex_single_hit, damage_str):
            shield_hitlag_range.append(singleHit(damage_str))

        elif re.match(regex_single_hit_diff, damage_str):
            shield_hitlag_range.append(singleHitDiff(damage_str))

        elif re.match(regex_multihit_same, damage_str):
            shield_hitlag_range.append(multiHitSame(damage_str))

        elif re.match(regex_multihit_diff, damage_str):
            shield_hitlag_range.append(multiHitDiff(damage_str))

        else:
            shield_hitlag_range.append("unknown Damage format")

    return shield_hitlag_range

def formula(damage):
    return floor(float(damage) * 0.3333334 + 3)

def singleHit(damage_str):
    return str(formula(damage_str))

def singleHitDiff(damage_str):
    damage = re.findall("\d+", damage_str)
    s_hitlag = [str(formula(d)) for d in damage]
    return "".join(["{}/".format(s) for s in s_hitlag[:-1]] + [s_hitlag[-1]])

def multiHitSame(damage_str):
    damage_sum, damage_per_hit, num_hits = re.findall("\d+", damage_str)
    s_hitlag_per_hit = formula(damage_per_hit)
    s_hitlag_sum = s_hitlag_per_hit * int(num_hits)

    s_hitlag_str = damage_str
    return "{} ({}*{})".format(s_hitlag_sum, s_hitlag_per_hit, num_hits)

def multiHitDiff(damage_str):
    damage_vals = re.findall("\d+", damage_str)

    s_hitlag_nums = [formula(d) for d in damage_vals[1:]]
    s_hitlag_sum = str(sum(s_hitlag_nums))
    s_hitlag_vals = [str(s_hitlag_sum)] + [str(n) for n in s_hitlag_nums]

    searched_index = 0
    shield_hitlag_str = damage_str
    for d, s in zip(damage_vals, s_hitlag_vals):
        shield_hitlag_str = \
            shield_hitlag_str[:searched_index] \
            + shield_hitlag_str[searched_index:].replace(d, "".join(s), 1)

        searched_index = shield_hitlag_str.index(s, searched_index) + len(s)

    return shield_hitlag_str

def makeValueRanges(ranges):
    ranges = [[[v] for v in r] for r in ranges]
    value_ranges = []
    for i, d in enumerate(ranges):
        sheet_info = {"range": "{}!H4:H".format(api.sheet_names[i]),
                      "majorDimension": "ROWS",
                      "values": d}
        value_ranges.append(sheet_info)
    return value_ranges

def writevalueRanges(value_ranges):
    request_body = {
        "value_input_option": "USER_ENTERED",
        "data": value_ranges
    }

    request = api.value_request.batchUpdate(spreadsheetId=api.sheet_id,
                                            body=request_body)
    response = request.execute()

    print("wrote values!")

def main():
    damage_ranges = getDamage()
    shield_hitlag_data = [calculateShieldHitlag(sum(d, []))
                            for d in damage_ranges]

    shield_hitlag_ranges = makeValueRanges(shield_hitlag_data)
    writevalueRanges(shield_hitlag_ranges)

if __name__ == '__main__':
    main()
