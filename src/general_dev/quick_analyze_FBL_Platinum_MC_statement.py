import camelot
import sys


fbl_statement_file = "D:\\TBD\\Download\\552233XXXXXX4759_15102020_15112020_50616231.pdf"

tables = camelot.read_pdf(fbl_statement_file)

if tables.n == 0:
    sys.exit("No tables could be extracted from this statement PDF file")

print("Total number of tables extracted: ", tables.n)
print(len(tables[0].df))

df = tables[0].df

for i in range(len(df)):
    print(df.iloc[i, 0], df.iloc[i, 2])

    if df.iloc[i, 0]
