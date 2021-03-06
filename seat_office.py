import random
import itertools

in_file = open('e_igloos.txt', 'r')
lines = in_file.readlines()

dimensions = [int(lines[0].split(' ')[0]),int(lines[0].split(' ')[1])]
dev_count_index = dimensions[1]+1
no_devs = int(lines[dev_count_index])
man_count_index = dev_count_index + no_devs + 1
no_mans = int(lines[man_count_index])

tables_raw = lines[1:dimensions[1]+1]
devs_raw = lines[(dev_count_index+1):(dev_count_index+1+no_devs)]
mans_raw = lines[(man_count_index+1):(man_count_index+1+no_mans)]

devs = []

for dev in devs_raw:
  company = dev.split(' ')[0]
  bonus = int(dev.split(' ')[1])
  skills = dev.split(' ')[3:]
  skill_set = set()
  for skill in skills:
    skill = skill.strip()
    skill_set.add(skill)
  devs.append({
    "skills": skill_set,
    "company": company,
    "bonus": bonus
  })

mans = []

for man in mans_raw:
  company = man.split(' ')[0]
  bonus = int(man.split(' ')[1])
  mans.append({
    "company": company,
    "bonus": bonus
  })

seat_plan = []

for i in range(dimensions[1]):
  seat_plan.append([])
  for j in range(dimensions[0]):
    curr = tables_raw[i][j]
    if curr == '#': seat_plan[i].append(None)
    elif curr == 'M': seat_plan[i].append({"type": True, "employee": None})
    elif curr == '_': seat_plan[i].append({"type": False, "employee": None})

adjacencies = []
seat_list = []

available_seats = 0
available_seats_dev = 0
available_seats_man = 0

for i in range(len(seat_plan)-1):
  for j in range(len(seat_plan[i])-1):
    if seat_plan[i][j]==None: 
      continue
    seat_list.append(seat_plan[i][j])
    available_seats += 1
    if seat_plan[i][j]["type"]:
      available_seats_man += 1
    else:
      available_seats_dev += 1
    k = i+1
    l = j
    if seat_plan[k][l] != None: 
      adjacencies.append(((i,j),(k,l)))
    k = i
    l = j+1
    if seat_plan[k][l] != None: 
      adjacencies.append(((i,j),(k,l)))

print("SIZE: ", dimensions)

print("DEV SEATS {}, DEVS {}".format(available_seats_dev, len(devs)))
print("MAN SEATS {}, MANS {}".format(available_seats_man, len(mans)))

best = []
max_score = 0

def do(seats):
  global max_score
  global best
  global mans
  global devs
  for seat in seat_list:
    if seat['type']:
      if not mans:
        continue
      seat['employee'] = mans.pop()
    else:
      if not devs:
        continue
      seat['employee'] = devs.pop()

  score = 0

  for adj in adjacencies:
    t1, t2 = adj
    t1i, t1j = t1
    t2i, t2j = t1
    e1 = seat_plan[t1i][t1j]
    e2 = seat_plan[t2i][t2j]
    if e1["employee"] is None or e2["employee"] is None or e1 is None or e2 is None:
      print(e1,e2)
      return

    if e1["employee"]["company"] == e1["employee"]["company"]:
      score += e1["employee"]["bonus"]*e2["employee"]["bonus"]
    if not e1["type"] and not e2["type"]:
      score += len(e1["employee"]["skills"].intersection(e2["employee"]["skills"]))*len(e1["employee"]["skills"].union(e2["employee"]["skills"]))

  if score > max_score:
    print(score)
    best = seat_plan
    max_score = score

seat_perms = itertools.permutations(seat_list)
print()
for seat_p in seat_perms:
  do(seat_p)

print(seat_plan)
print("SCORE: ", max_score)