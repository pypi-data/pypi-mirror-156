def parse_table(el):
    columns = []
    for th in el.thead.tr.children:
        columns.append(th.text)
    rows = []
    for tr in el.tbody.children:
        row = {}
        for i, td in enumerate(tr.children):
            row[columns[i]] = td.text
        rows.append(row)
    return rows
