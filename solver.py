from ortools.sat.python import cp_model
import pandas as pd
import math

MI_COUNTY_COORDS = {
    'Alcona': (44.6694, -83.1827), 'Alger': (46.4468, -86.5373), 'Allegan': (42.5906, -85.8908),
    'Alpena': (45.0650, -83.4327), 'Antrim': (45.0164, -85.1561), 'Arenac': (44.0417, -83.9127),
    'Baraga': (46.7611, -88.4937), 'Barry': (42.5994, -85.3089), 'Bay': (43.6961, -83.9838),
    'Benzie': (44.6028, -86.0875), 'Berrien': (41.9275, -86.4228), 'Branch': (41.9133, -85.0625),
    'Calhoun': (42.2450, -85.0011), 'Cass': (41.9133, -85.9942), 'Charlevoix': (45.3436, -85.1738),
    'Cheboygan': (45.5700, -84.4810), 'Chippewa': (46.3939, -84.5819), 'Clare': (43.9861, -84.8441),
    'Clinton': (42.9436, -84.5994), 'Crawford': (44.6833, -84.6050), 'Delta': (45.8006, -86.9141),
    'Dickinson': (46.0042, -87.8730), 'Eaton': (42.5994, -84.8413), 'Emmet': (45.5528, -84.9538),
    'Genesee': (43.0128, -83.6927), 'Gladwin': (43.9861, -84.3619), 'Gogebic': (46.4928, -89.8627),
    'Grand Traverse': (44.7436, -85.5644), 'Gratiot': (43.2961, -84.5994), 'Hillsdale': (41.9133, -84.5994),
    'Houghton': (47.0042, -88.6064), 'Huron': (43.9275, -83.0605), 'Ingham': (42.5994, -84.3619),
    'Ionia': (42.9436, -85.0625), 'Iosco': (44.3019, -83.5189), 'Iron': (46.2100, -88.5214),
    'Isabella': (43.6294, -84.8441), 'Jackson': (42.2450, -84.4022), 'Kalamazoo': (42.2450, -85.5364),
    'Kalkaska': (44.7297, -85.1611), 'Kent': (43.0128, -85.5364), 'Keweenaw': (47.4500, -88.0900),
    'Lake': (43.9861, -85.8200), 'Lapeer': (43.0997, -83.2188), 'Leelanau': (45.0653, -85.7703),
    'Lenawee': (41.9136, -84.0478), 'Livingston': (42.5994, -83.9127), 'Luce': (46.4736, -85.4892),
    'Mackinac': (46.0897, -84.7478), 'Macomb': (42.6700, -82.9200), 'Manistee': (44.2972, -86.0875),
    'Marquette': (46.5503, -87.6536), 'Mason': (43.9861, -86.0875), 'Mecosta': (43.6294, -85.3089),
    'Menominee': (45.5275, -87.5817), 'Midland': (43.6294, -84.3619), 'Missaukee': (44.3019, -85.1053),
    'Monroe': (41.9136, -83.4889), 'Montcalm': (43.2961, -85.1053), 'Montmorency': (45.0306, -84.1353),
    'Muskegon': (43.3550, -86.1089), 'Newaygo': (43.6294, -85.8200), 'Oakland': (42.6564, -83.3816),
    'Oceana': (43.6586, -86.2142), 'Ogemaw': (44.3019, -84.1353), 'Ontonagon': (46.7972, -89.1700),
    'Osceola': (43.9861, -85.3089), 'Oscoda': (44.6833, -84.1353), 'Otsego': (45.0306, -84.6050),
    'Ottawa': (42.9436, -86.0031), 'Presque Isle': (45.4306, -83.9403), 'Roscommon': (44.3019, -84.6050),
    'Saginaw': (43.3550, -84.0478), 'St. Clair': (42.9158, -82.6761), 'St. Joseph': (41.9133, -85.5364),
    'Sanilac': (43.4275, -82.9478), 'Schoolcraft': (46.1469, -86.2514), 'Shiawassee': (42.9436, -84.1353),
    'Tuscola': (43.4964, -83.3703), 'Van Buren': (42.2450, -86.0031), 'Washtenaw': (42.2722, -83.9872),
    'Wayne': (42.2814, -83.1883), 'Wexford': (44.3019, -85.5644),
    'Detroit': (42.3314, -83.0458),  # city-level, separate from Wayne County
}

df = pd.read_csv("data/filtered_output.csv")

df['covg4313314'] = pd.to_numeric(df['covg4313314'], errors='coerce')
df['pop19_35'] = pd.to_numeric(df['pop19_35'], errors='coerce')
df['unvacc'] = (df['pop19_35'] * (100 - df['covg4313314']) / 100).round(0).astype(int)
df['weight_int'] = (100 - df['covg4313314']).round(0).astype(int)
df = df.sort_values('cntyname').reset_index(drop=True)

ALPHA = 20          # max vaccinations per visit (achieved in high-coverage counties)
B = 3001            # total visit budget
MIN_COVERAGE = 0.05 # each county must address at least 5% of its unvaccinated kids
MAX_COVERAGE = 0.90 # herd-immunity cap

# county-specific alpha: lower coverage = harder to convince = fewer vaccinations per visit
df['alpha'] = (ALPHA * df['covg4313314'] / 100).round(0).clip(lower=1).astype(int)

model = cp_model.CpModel()
n = len(df)

x = [model.NewIntVar(0, max(0, int(MAX_COVERAGE * df.loc[i, 'unvacc'] / df.loc[i, 'alpha'])), f"x_{i}") for i in range(n)]

# budget
model.Add(sum(x) <= B)

# each county must address at least 5% of its unvaccinated kids
for i in range(n):
    alpha_i = int(df.loc[i, 'alpha'])
    unvacc_i = int(df.loc[i, 'unvacc'])
    max_visits = int(MAX_COVERAGE * unvacc_i / alpha_i)
    min_visits = min(max_visits, math.ceil(MIN_COVERAGE * unvacc_i / alpha_i))
    model.Add(x[i] >= min_visits)

# weighted objective: prioritize most-unvaccinated counties
model.Minimize(sum(
    int(df.loc[i, 'weight_int']) * (int(df.loc[i, 'unvacc']) - int(df.loc[i, 'alpha']) * x[i])
    for i in range(n)
))

solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL:
    total_visits = sum(solver.Value(x[i]) for i in range(n))
    total_vacc = sum(solver.Value(x[i]) * int(df.loc[i, 'alpha']) for i in range(n))
    total_remaining = sum(
        int(df.loc[i, 'unvacc']) - solver.Value(x[i]) * int(df.loc[i, 'alpha'])
        for i in range(n)
    )
    print(f"Objective: {solver.ObjectiveValue():.0f} (weighted unvaccinated remaining)")
    print(f"Total visits used:      {total_visits} / {B}")
    print(f"Total vaccinated:       {total_vacc}")
    print(f"Unvaccinated remaining: {total_remaining}")
    print(f"\nAllocations:")
    results = []
    for i in range(n):
        v = solver.Value(x[i])
        a = int(df.loc[i, 'alpha'])
        vacc = v * a
        pop = df.loc[i, 'pop19_35']
        old_covg = df.loc[i, 'covg4313314']
        new_covg = min(100.0, old_covg + (vacc / pop * 100))
        print(f"  {df.loc[i,'cntyname']:<20} visits={v:<5}  {old_covg:5.1f}% -> {new_covg:5.1f}%")
        county = df.loc[i, 'cntyname']
        lat, lon = MI_COUNTY_COORDS.get(county, (None, None))
        results.append({
            'cntyname': county,
            'lat': lat,
            'lon': lon,
            'visits': v,
            'alpha': a,
            'vaccinated': vacc,
            'unvacc': df.loc[i, 'unvacc'],
            'old_coverage_pct': round(old_covg, 2),
            'new_coverage_pct': round(new_covg, 2),
        })
    pd.DataFrame(results).to_csv("data/3001_solver_output.csv", index=False)
    print("\nSaved to data/3001_solver_output.csv")
else:
    print("No optimal solution found")
