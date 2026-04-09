from ortools.sat.python import cp_model
import pandas as pd
import math

df = pd.read_csv("data/filtered_output.csv")

df['covg4313314'] = pd.to_numeric(df['covg4313314'], errors='coerce')
df['pop19_35'] = pd.to_numeric(df['pop19_35'], errors='coerce')
df['unvacc'] = (df['pop19_35'] * (100 - df['covg4313314']) / 100).round(0).astype(int)
df['cap'] = df['unvacc'].apply(lambda x: math.ceil(x / 20))
df['weight_int'] = (100 - df['covg4313314']).round(0).astype(int)
df = df.sort_values('cntyname').reset_index(drop=True)

ALPHA = 20          # vaccinations per visit
B = 1500            # total visit budget
MIN_COVERAGE = 0.05 # each county must address at least 5% of its unvaccinated kids

model = cp_model.CpModel()
n = len(df)

x = [model.NewIntVar(0, int(df.loc[i, 'cap']), f"x_{i}") for i in range(n)]

# budget
model.Add(sum(x) <= B)

# equity: each county must cover at least MIN_COVERAGE fraction of its unvaccinated kids
for i in range(n):
    min_visits = math.ceil(MIN_COVERAGE * df.loc[i, 'unvacc'] / ALPHA)
    model.Add(x[i] >= min_visits)

# weighted objective: prioritize low-coverage counties (weights scaled x100 for integer requirement)
model.Minimize(sum(
    int(df.loc[i, 'weight_int']) * (int(df.loc[i, 'unvacc']) - ALPHA * x[i])
    for i in range(n)
))

solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL:
    total_visits = sum(solver.Value(x[i]) for i in range(n))
    total_vacc = total_visits * ALPHA
    print(f"Objective: {solver.ObjectiveValue():.0f} (weighted unvaccinated remaining, scaled x100)")
    print(f"Total visits used: {total_visits} / {B}")
    print(f"Total vaccinated:  {total_vacc}")
    print(f"\nAllocations:")
    results = []
    for i in range(n):
        v = solver.Value(x[i])
        print(f"  {df.loc[i,'cntyname']:<20} visits={v:<5}  vaccinated={v*ALPHA:<6}  unvacc={df.loc[i,'unvacc']}")
        results.append({
            'cntyname': df.loc[i, 'cntyname'],
            'visits': v,
            'vaccinated': v * ALPHA,
            'unvacc': df.loc[i, 'unvacc'],
            'coverage_pct': df.loc[i, 'covg4313314'],
        })
    pd.DataFrame(results).to_csv("data/solver_output.csv", index=False)
    print("\nSaved to data/solver_output.csv")
else:
    print("No optimal solution found")
