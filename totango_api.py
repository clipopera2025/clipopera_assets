import os
import argparse
import json
import requests


class TotangoAPI:
    """Simple client for the Totango REST API."""

    def __init__(self, base_url: str, api_token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    def get_touchpoint_types(self) -> dict:
        """Return available touchpoint types."""
        url = f"{self.base_url}/api/v3/touchpoint-types"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def post_account(self, account_payload: dict) -> dict:
        """Create or update an account."""
        url = f"{self.base_url}/int-hub/api/v1/accounts"
        response = requests.post(url, json=account_payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    # --- Logs & Monitoring ---
    def get_audit_log(self) -> dict:
        """Return audit logs."""
        url = f"{self.base_url}/api/v2/auditlog"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_events(self, account_id: str) -> dict:
        """Return account events."""
        url = f"{self.base_url}/api/v2/accounts/{account_id}/events"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    # --- Objectives & Planning ---
    def get_objective_status(self) -> dict:
        url = f"{self.base_url}/api/v2/objectives/status"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_objective_category(self) -> dict:
        url = f"{self.base_url}/api/v2/objectives/category"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_plan_summary(self, account_id: str) -> dict:
        url = f"{self.base_url}/api/v2/accounts/{account_id}/plans/summary"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_outcome_report(self, sbid: str, account_id: str) -> dict:
        url = f"{self.base_url}/api/v2/plans/{sbid}/account/{account_id}/outcome"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    # --- Automations ---
    def run_successplay(self, json_path: str) -> dict:
        url = f"{self.base_url}/api/v2/successplay/run"
        with open(json_path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        resp = requests.post(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    # --- SCIM Identity Management ---
    def get_scim_users(self, service_id: str) -> dict:
        url = f"{self.base_url}/api/v2/scim/{service_id}/Users"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_scim_groups(self, service_id: str) -> dict:
        url = f"{self.base_url}/api/v2/scim/{service_id}/Groups"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_scim_user(self, service_id: str, user_id: str) -> dict:
        url = f"{self.base_url}/api/v2/scim/{service_id}/Users/{user_id}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_scim_group(self, service_id: str, team_id: str) -> dict:
        url = f"{self.base_url}/api/v2/scim/{service_id}/Groups/{team_id}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def create_scim_user(self, service_id: str, json_path: str) -> dict:
        url = f"{self.base_url}/api/v2/scim/{service_id}/Users"
        with open(json_path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        resp = requests.post(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def update_scim_user(
        self, service_id: str, user_id: str, json_path: str, method: str = "PUT"
    ) -> dict:
        url = f"{self.base_url}/api/v2/scim/{service_id}/Users/{user_id}"
        with open(json_path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        method = method.upper()
        if method == "PATCH":
            resp = requests.patch(url, json=payload, headers=self.headers)
        else:
            resp = requests.put(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def delete_scim_user(self, service_id: str, user_id: str) -> None:
        url = f"{self.base_url}/api/v2/scim/{service_id}/Users/{user_id}"
        resp = requests.delete(url, headers=self.headers)
        resp.raise_for_status()

    def update_scim_group(
        self, service_id: str, team_id: str, json_path: str, method: str = "PUT"
    ) -> dict:
        url = f"{self.base_url}/api/v2/scim/{service_id}/Groups/{team_id}"
        with open(json_path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        method = method.upper()
        if method == "PATCH":
            resp = requests.patch(url, json=payload, headers=self.headers)
        else:
            resp = requests.put(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def delete_scim_group(self, service_id: str, team_id: str) -> None:
        url = f"{self.base_url}/api/v2/scim/{service_id}/Groups/{team_id}"
        resp = requests.delete(url, headers=self.headers)
        resp.raise_for_status()


def main() -> None:
    parser = argparse.ArgumentParser(description="Totango API helper")
    parser.add_argument("--base_url", required=True, help="Base URL for the API")
    parser.add_argument(
        "--token",
        default=os.getenv("TOTANGO_API_TOKEN"),
        help="API token or set TOTANGO_API_TOKEN",
    )
    parser.add_argument(
        "--get_touchpoints", action="store_true", help="Fetch touchpoint types"
    )
    parser.add_argument(
        "--account", help="Path to JSON file describing an account to create"
    )

    # Logs & Monitoring
    parser.add_argument(
        "--get_audit_log", action="store_true", help="Retrieve audit log"
    )
    parser.add_argument(
        "--get_events", metavar="ACCOUNT_ID", help="Retrieve events for an account"
    )

    # Objectives & Planning
    parser.add_argument(
        "--get_objective_status", action="store_true", help="Get objective statuses"
    )
    parser.add_argument(
        "--get_objective_category", action="store_true", help="Get objective categories"
    )
    parser.add_argument(
        "--get_plan_summary", metavar="ACCOUNT_ID", help="Get plan summary for account"
    )
    parser.add_argument(
        "--get_outcome_report",
        nargs=2,
        metavar=("SBID", "ACCOUNT_ID"),
        help="Get outcome report",
    )

    # Automations
    parser.add_argument(
        "--run_successplay", metavar="JSON", help="Run SuccessPlay from JSON file"
    )

    # SCIM Identity Management
    parser.add_argument(
        "--get_scim_users", metavar="SERVICE_ID", help="List SCIM users"
    )
    parser.add_argument(
        "--get_scim_groups", metavar="SERVICE_ID", help="List SCIM groups"
    )
    parser.add_argument(
        "--get_scim_user",
        nargs=2,
        metavar=("SERVICE_ID", "USER_ID"),
        help="Get SCIM user",
    )
    parser.add_argument(
        "--get_scim_group",
        nargs=2,
        metavar=("SERVICE_ID", "TEAM_ID"),
        help="Get SCIM group",
    )
    parser.add_argument(
        "--create_scim_user",
        nargs=2,
        metavar=("SERVICE_ID", "JSON"),
        help="Create SCIM user",
    )
    parser.add_argument(
        "--update_scim_user",
        nargs="+",
        metavar=("SERVICE_ID", "USER_ID", "JSON", "METHOD"),
        help="Update SCIM user",
    )
    parser.add_argument(
        "--delete_scim_user",
        nargs=2,
        metavar=("SERVICE_ID", "USER_ID"),
        help="Delete SCIM user",
    )
    parser.add_argument(
        "--update_scim_group",
        nargs="+",
        metavar=("SERVICE_ID", "TEAM_ID", "JSON", "METHOD"),
        help="Update SCIM group",
    )
    parser.add_argument(
        "--delete_scim_group",
        nargs=2,
        metavar=("SERVICE_ID", "TEAM_ID"),
        help="Delete SCIM group",
    )

    args = parser.parse_args()

    if not args.token:
        parser.error("API token is required via --token or TOTANGO_API_TOKEN")

    api = TotangoAPI(args.base_url, args.token)

    if args.get_touchpoints:
        data = api.get_touchpoint_types()
        print(json.dumps(data, indent=2))

    if args.account:
        with open(args.account, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        data = api.post_account(payload)
        print(json.dumps(data, indent=2))

    if args.get_audit_log:
        data = api.get_audit_log()
        print(json.dumps(data, indent=2))

    if args.get_events:
        data = api.get_events(args.get_events)
        print(json.dumps(data, indent=2))

    if args.get_objective_status:
        data = api.get_objective_status()
        print(json.dumps(data, indent=2))

    if args.get_objective_category:
        data = api.get_objective_category()
        print(json.dumps(data, indent=2))

    if args.get_plan_summary:
        data = api.get_plan_summary(args.get_plan_summary)
        print(json.dumps(data, indent=2))

    if args.get_outcome_report:
        sbid, acc = args.get_outcome_report
        data = api.get_outcome_report(sbid, acc)
        print(json.dumps(data, indent=2))

    if args.run_successplay:
        data = api.run_successplay(args.run_successplay)
        print(json.dumps(data, indent=2))

    if args.get_scim_users:
        data = api.get_scim_users(args.get_scim_users)
        print(json.dumps(data, indent=2))

    if args.get_scim_groups:
        data = api.get_scim_groups(args.get_scim_groups)
        print(json.dumps(data, indent=2))

    if args.get_scim_user:
        service_id, user_id = args.get_scim_user
        data = api.get_scim_user(service_id, user_id)
        print(json.dumps(data, indent=2))

    if args.get_scim_group:
        service_id, team_id = args.get_scim_group
        data = api.get_scim_group(service_id, team_id)
        print(json.dumps(data, indent=2))

    if args.create_scim_user:
        service_id, file_path = args.create_scim_user
        data = api.create_scim_user(service_id, file_path)
        print(json.dumps(data, indent=2))

    if args.update_scim_user:
        service_id, user_id, file_path, *method = args.update_scim_user
        method = method[0] if method else "PUT"
        data = api.update_scim_user(service_id, user_id, file_path, method)
        print(json.dumps(data, indent=2))

    if args.delete_scim_user:
        service_id, user_id = args.delete_scim_user
        api.delete_scim_user(service_id, user_id)
        print("Deleted SCIM user")

    if args.update_scim_group:
        service_id, team_id, file_path, *method = args.update_scim_group
        method = method[0] if method else "PUT"
        data = api.update_scim_group(service_id, team_id, file_path, method)
        print(json.dumps(data, indent=2))

    if args.delete_scim_group:
        service_id, team_id = args.delete_scim_group
        api.delete_scim_group(service_id, team_id)
        print("Deleted SCIM group")


if __name__ == "__main__":
    main()
