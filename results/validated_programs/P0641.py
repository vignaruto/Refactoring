def machine_utilisation(logs, shift_minutes):
    report = {}
    for machine, shifts in logs.items():
        rates = []
        for run, setup, idle in shifts:
            utilisation = (run - 0.5 * setup) / (shift_minutes - idle) if shift_minutes > idle else 0.0
            rates.append(round(utilisation, 3))
        report[machine] = rates
    return report

if __name__ == "__main__":
    logs = {"m1": [(300, 40, 60), (100, 0, 480)]}
    assert machine_utilisation(logs, 480) == {"m1": [0.667, 0.0]}
