import sqlite3
conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()
print('TABLES:')
for row in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    print(row[0])
print('--- departments data ---')
try:
    for row in c.execute('SELECT id, name, slug, category, is_active FROM public_admin_department'):
        print(row)
except Exception as e:
    print('table missing or query failed:', e)
conn.close()
