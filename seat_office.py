import random
import itertools
from sqlite3 import connect

# For an in-memory only database:
db = connect(':memory:')
db_cursor = db.cursor()

statement = 'CREATE TABLE IF NOT EXISTS employees (eid INTEGER PRIMARY KEY, company TEXT, type INTEGER, bonus INTEGER, skills TEXT)'
db_cursor.execute(statement)  

statement = 'CREATE TABLE IF NOT EXISTS synergies (e1 INTEGER, e2 INTEGER, potential INTEGER, FOREIGN KEY(e1) REFERENCES employees(eid), FOREIGN KEY(e2) REFERENCES employees(eid))'
db_cursor.execute(statement)  

statement = 'CREATE TABLE IF NOT EXISTS seats (sid INTEGER PRIMARY KEY, coord1 INTEGER, coord2 INTEGER, type INTEGER, taken BOOLEAN)'
db_cursor.execute(statement)  

statement = 'CREATE TABLE IF NOT EXISTS neighbours (s1 INTEGER, s2 INTEGER, potential INTEGER, FOREIGN KEY(s1) REFERENCES seats(sid), FOREIGN KEY(s2) REFERENCES seats(sid))'
db_cursor.execute(statement)

statement = 'CREATE TABLE IF NOT EXISTS seat_map (sid INTEGER, eid INTEGER, FOREIGN KEY(sid) REFERENCES seats(sid), FOREIGN KEY(eid) REFERENCES employees(eid))'
db_cursor.execute(statement)  

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

print('EMPLOYEES: ', db_cursor.execute('SELECT COUNT(*) FROM employees').fetchone()[0])

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

print('SEATS: ', db_cursor.execute('SELECT COUNT(*) FROM seats').fetchone()[0])

all_seats = db_cursor.execute('SELECT * FROM seats').fetchall()

for seat in all_seats:
  coord1 = seat[1]
  coord2 = seat[2]

  right_neighbour = db_cursor.execute('SELECT sid FROM seats WHERE coord1 = ? AND coord2 = ?', (coord1+1, coord2)).fetchone()
  if right_neighbour is not None:
    db_cursor.execute("INSERT INTO neighbours (s1, s2) VALUES (?,?)", (seat[0], right_neighbour[0]))
    db_cursor.execute("INSERT INTO neighbours (s1, s2) VALUES (?,?)", (right_neighbour[0], seat[0]))
  bottom_neighbour = db_cursor.execute('SELECT sid FROM seats WHERE coord1 = ? AND coord2 = ?', (coord1, coord2+1)).fetchone()
  if bottom_neighbour is not None:
    db_cursor.execute("INSERT INTO neighbours (s1, s2) VALUES (?,?)", (seat[0], bottom_neighbour[0]))
    db_cursor.execute("INSERT INTO neighbours (s1, s2) VALUES (?,?)", (bottom_neighbour[0], seat[0]))

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

score = 0

rows = db_cursor.execute('SELECT e1.eid, e1.type, e2.eid, e2.type, s.potential FROM synergies s JOIN employees e1 ON e1.eid = s.e1 JOIN employees e2 ON e2.eid = s.e2 WHERE s.potential > 0 ORDER BY s.potential DESC').fetchall()

for syn in rows:
  statement = "SELECT n.s1, s1.type, n.s2, s2.type FROM neighbours n"\
    " JOIN seats s1 ON n.s1 = s1.sid"\
    " JOIN seats s2 ON n.s2 = s2.sid"\
    " WHERE ((s1.type = ? AND s2.type = ?) OR (s2.type = ? AND s1.type = ?))"\
    " AND (NOT EXISTS (SELECT * FROM seat_map sm WHERE sm.sid = s1.sid OR sm.sid = s2.sid))"
  adj = db_cursor.execute(statement,(syn[1], syn[3], syn[3], syn[1])).fetchone()
  if adj is not None:
    score += syn[4]
    if adj[1] == syn[1] and adj[3] == syn[3]:
      db_cursor.executemany('INSERT INTO seat_map (sid, eid) VALUES (?,?)', [(adj[0], syn[0]), (adj[2], syn[2])])
    elif adj[1] == syn[3] and adj[3] == syn[1]:
      print("B")
      db_cursor.executemany('INSERT INTO seat_map (sid, eid) VALUES (?,?)', [(adj[0], syn[2]), (adj[2], syn[0])])
    else:
      print('HOW TF DID THAT HAPPEN?')
print(score)