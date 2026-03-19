import json
import os


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def determine_action(issue, driver):
    issue = issue.lower()

    if "idle" in issue and driver == "EC2":
        return "Terminate or downsize instance"
    if "unused" in issue and driver == "S3":
        return "Archive or delete unused storage"
    if "underutilized" in issue and driver == "RDS":
        return "Rightsize database instance"

    return "Review resource"


def determine_priority(savings):
    if savings >= 400:
        return "high"
    elif savings >= 200:
        return "medium"
    else:
        return "low"


def build_action_plan(findings, owners):
    results = []

    for item in findings:
        service = item.get("service")
        owner_info = owners.get(service, {"owner": "unassigned", "contact": "unknown"})

        savings = item.get("estimated_monthly_savings", 0)

        results.append({
            "driver": item.get("driver"),
            "issue": item.get("issue"),
            "resource": item.get("resource"),
            "service": service,
            "owner": owner_info["owner"],
            "contact": owner_info["contact"],
            "recommended_action": determine_action(item.get("issue"), item.get("driver")),
            "priority": determine_priority(savings),
            "estimated_monthly_savings": savings,
            "status": "open"
        })

    return results


def main():
    findings = load_json("data/findings.json")
    owners = load_json("data/owners.json")

    action_plan = build_action_plan(findings, owners)

    output = {"action_items": action_plan}

    save_json(output, "output/action_plan.json")

    print("\n✅ Action plan generated")
    print(json.dumps(output, indent=4))


if __name__ == "__main__":
    main()
