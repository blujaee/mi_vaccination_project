# Michigan Vaccination Resource Allocation Model

An integer programming model to optimally allocate mobile vaccination clinic visits 
across Michigan's 83 counties and Detroit, minimizing the weighted number of 
unvaccinated children remaining after deployment.

Built for ISE 3330: Engineering Operations Research Final Project, Oakland University, April 2026.

## Problem

As of Q4 2025, only 66.55% of Michigan children aged 19–35 months have completed 
the recommended 4313314 vaccine series (DTaP, Polio, MMR, Hib, HepB, Varicella, PCV).
This rate well below the 90–95% herd immunity threshold. This model determines how a fixed 
budget of mobile clinic visits should be distributed across counties to maximize 
public health impact.

## Model

The objective minimizes the total weighted unvaccinated children remaining:

minimize Z = Σ wᵢ(Uᵢ - αᵢxᵢ)

Where xᵢ is visits allocated to county i, wᵢ is the incomplete rate weight, 
Uᵢ is unvaccinated children, and αᵢ is county-specific vaccination yield per visit.

Constraints:
- Budget: total visits ≤ B
- Equity floor: each county addresses at least 5% of its unvaccinated population
- Herd immunity cap: no county exceeds 90% coverage of its unvaccinated pool
- Integrality: xᵢ ∈ Z≥0

Solved using Google OR-Tools CP-SAT solver.

## Results Overviwe

| Budget | Vaccinated | % of Backlog | Total Coverage | Herd Immunity |
|--------|------------|--------------|----------------|---------------|
| 500    | 5,936      | 12.1%        | 70.6%          | No            |
| 1,500  | 17,915     | 36.5%        | 78.7%          | No            |
| 3,000  | 38,212     | 77.9%        | 92.6%          | Yes           |

## Files

- `solver.py` — main integer programming model
- `clean_data.py` — data cleaning and preprocessing
- `data_stats.py` — exploratory data analysis
- `data/` — input data files
- `ISE 3330 Final Project.pdf` — full report

## Data Sources

- MDHHS County Immunization Report Cards (Q4 2025)
- 19–35 month population denominators obtained directly from MDHHS by request

## Requirements

```
pip install ortools pandas openpyxl
```
