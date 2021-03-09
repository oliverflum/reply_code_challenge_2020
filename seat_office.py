import random
import itertools
from sqlite3 import connect

# For an in-memory only database:
db = connect(':memory:')
db_cursor = db.cursor()

statement = 'CREATE TABLE IF NOT EXISTS employees (eid INTEGER PRIMARY KEY, company TEXT, type INTEGER, bonus INTEGER, skills TEXT)'
db_cursor.execute(statement)  # Returns None on create table

statement = 'CREATE TABLE IF NOT EXISTS synergies (e1 INTEGER, e2 INTEGER, potential INTEGER, FOREIGN KEY(e1) REFERENCES employees(eid), FOREIGN KEY(e2) REFERENCES employees(eid))'
db_cursor.execute(statement)  # Returns None on create table

statement = 'CREATE TABLE IF NOT EXISTS seats (sid INTEGER PRIMARY KEY, coord1 INTEGER, coord2 INTEGER, type INTEGER, taken BOOLEAN)'
db_cursor.execute(statement)  # Returns None on create table

statement = 'CREATE TABLE IF NOT EXISTS seat_map (sid INTEGER, eid INTEGER, FOREIGN KEY(sid) REFERENCES seats(sid), FOREIGN KEY(eid)) REFERENCES employees(eid))'
db_cursor.execute(statement)  # Returns None on create table

in_file = open('solar.txt', 'r')
lines = in_file.readlines()

dimensions = [int(lines[0].split(' ')[0]),int(lines[0].split(' ')[1])]
dev_count_index = dimensions[1]+1
no_devs = int(lines[dev_count_index])
man_count_index = dev_count_index + no_devs + 1
no_mans = int(lines[man_count_index])

tables_raw = lines[1:dimensions[1]+1]
devs_raw = lines[(dev_count_index+1):(dev_count_index+1+no_devs)]
mans_raw = lines[(man_count_index+1):(man_count_index+1+no_mans)]

for dev in devs_raw:
  company = dev.split(' ')[0]
  bonus = int(dev.split(' ')[1])
  skills = dev.split(' ')[3:]
  skill_set = set()
  for skill in skills:
    skill = skill.strip()
    skill_set.add(skill)
    statement = 'INSERT INTO employees (company, type, bonus, skills) VALUES (?,?,?,?)'
    db_cursor.execute(statement, (company, 0, bonus, ';'.join(list(skill_set))))

for man in mans_raw:
  company = man.split(' ')[0]
  bonus = int(man.split(' ')[1])
  statement = 'INSERT INTO employees (company, type, bonus) VALUES (?,?,?)'
  db_cursor.execute(statement, (company, 1, bonus))

for i in range(dimensions[1]):
  for j in range(dimensions[0]):
    curr = tables_raw[i][j]
    if curr == '#': continue
    elif curr == 'M': 
      statement = 'INSERT INTO seats (coord1, coord2, type) VALUES (?,?,?)'
      db_cursor.execute(statement, (i, j, 1))
    elif curr == '_': 
      statement = 'INSERT INTO seats (coord1, coord2, type) VALUES (?,?,?)'
      db_cursor.execute(statement, (i, j, 0))

print(db_cursor.execute('SELECT COUNT(*) FROM employees').fetchone()[0])

rows = db_cursor.execute('SELECT * FROM employees e1 LEFT JOIN employees e2 WHERE e1.eid < e2.eid').fetchall()
print(len(rows))
for row in rows:
    e1 = {
      "id": row[0],
      "company": row[1],
      "type": row[2],
      "bonus": row[3],
      "skills": set(';'.split(row[4]))
    }
    e2 = {
      "id": row[0+5],
      "company": row[1+5],
      "type": row[2+5],
      "bonus": row[3+5],
      "skills": set(';'.split(row[4+5]))
    }
    score = 0
    if e1["company"] == e2["company"]:
      score += e1["bonus"]*e2["bonus"]
    if e1["type"] == 0 and e2["type"] == 0:
      score += len(e1["skills"].intersection(e2["skills"]))*len(e1["skills"].union(e2["skills"]))
    statement = 'INSERT INTO synergies (e1, e2, potential) VALUES (?,?,?)'
    db_cursor.execute(statement, (e1["id"], e2["id"], score))