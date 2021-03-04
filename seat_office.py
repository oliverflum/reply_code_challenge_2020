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

avail_m_tables = []
avail_d_tables = []

for i in range(dimensions[1]):
  for j in range(dimensions[0]):
    curr = tables_raw[i][j]
    if curr == '#': continue
    elif curr == 'M': avail_m_tables.append((i,j))
    elif curr == '_': avail_d_tables.append((i,j))

all_skills = []

for dev in devs_raw:
  skills = dev.split(' ')[3:]
  for skill in skills:
    skill = skill.strip()
    if not skill in all_skills:
      all_skills.append(skill)
  company = dev.split(' ')[0]

devs = []

for dev in devs_raw:
  company = dev.split(' ')[0]
  bonus = dev.split(' ')[1]
  skills = dev.split(' ')[3:]
  skills_bin = [0] * len(all_skills)
  for skill in skills:
    skill = skill.strip()
    skills_bin[all_skills.index(skill)] = 1 
  devs.append({
    "skills": skills_bin,
    "company": company,
    "bonus": bonus
  })

mans = []

for man in mans_raw:
  company = man.split(' ')[0]
  bonus = man.split(' ')[1]
  mans.append({
    "company": company,
    "bonus": bonus
  })
