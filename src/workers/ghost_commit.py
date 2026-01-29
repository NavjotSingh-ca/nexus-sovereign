"""
Ghost-Commit Agent - Real GitHub Repository Hunter
Tracks actual commits, repos, and security issues at major tech companies
"""
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from github import Github

env_path = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(env_path)

class GhostCommitAgent:
    def __init__(self):
        self.agent_id = "ghost_commit_001"
        self.agent_type = "hunter"
        self.name = "Ghost-Commit"
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        # Initialize GitHub API (public access, no token needed for basic queries)
        self.github = Github()  # Public API access
        
    def log(self, message):
        print(f"[{self.name}] {message}")
        
    def write_to_ledger(self, message_type, payload):
        """Write findings to ledger"""
        try:
            from supabase import create_client
            supabase = create_client(self.supabase_url, self.supabase_key)
            
            data = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "message_type": message_type,
                "payload": payload,
                "status": "pending"
            }
            
            supabase.table("ledger").insert(data).execute()
            self.log(f"Written to ledger: {message_type}")
            
        except Exception as e:
            self.log(f"ERROR writing to ledger: {e}")
            
    def scan_github_org(self, org_name):
        """Scan real GitHub organization for repository activity"""
        self.log(f"HUNTING: {org_name} on GitHub")
        
        try:
            org = self.github.get_organization(org_name)
            
            # Get recent repositories (last 30 days)
            repos = []
            secret_keywords = []
            suspicious_commits = []
            
            for repo in org.get_repos(sort="updated", direction="desc")[:10]:
                repo_data = {
                    "name": repo.name,
                    "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "language": repo.language,
                    "description": repo.description or ""
                }
                repos.append(repo_data)
                
                # Check description for security keywords
                if repo.description:
                    desc_lower = repo.description.lower()
                    if any(keyword in desc_lower for keyword in ['api-key', 'password', 'secret', 'internal', 'private']):
                        secret_keywords.append(repo.name)
                        
                # Check recent commits for suspicious activity
                try:
                    commits = repo.get_commits(since=datetime.now() - timedelta(days=7))[:5]
                    for commit in commits:
                        commit_msg = commit.commit.message.lower()
                        if any(keyword in commit_msg for keyword in ['fix', 'patch', 'security', 'urgent']):
                            suspicious_commits.append({
                                "repo": repo.name,
                                "message": commit.commit.message[:100],
                                "author": commit.author.login if commit.author else "Unknown"
                            })
                except:
                    pass  # Skip repos we can't access
                    
            # Determine alert level
            alert_level = "LOW"
            if len(secret_keywords) > 0:
                alert_level = "HIGH"
            elif len(suspicious_commits) > 0:
                alert_level = "MEDIUM"
                
            findings = {
                "org": org_name,
                "timestamp": datetime.now().isoformat(),
                "new_repos": len(repos),
                "repos": repos[:5],  # First 5 only
                "secret_keywords": secret_keywords,
                "suspicious_commits": suspicious_commits[:3],  # First 3 only
                "alert_level": alert_level,
                "total_stars": sum(repo["stars"] for repo in repos),
                "primary_language": repos[0]["language"] if repos else "Unknown"
            }
            
            self.log(f"Found: {len(repos)} repos | {len(secret_keywords)} security issues | {len(suspicious_commits)} suspicious commits")
            
            return findings
            
        except Exception as e:
            self.log(f"Hunt failed for {org_name}: {e}")
            return {
                "org": org_name,
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e),
                "alert_level": "UNKNOWN"
            }
            
    def run(self):
        """Main execution - hunt real GitHub organizations"""
        self.log("="*50)
        self.log("GHUB HUNTER - REAL INTELLIGENCE GATHERING")
        self.log("="*50)
        
        # Real tech companies to hunt
        targets = [
            "microsoft",
            "google", 
            "apple",
            "amazon",
            "meta",
            "openai",
            "anthropics",
            "netflix",
            "spotify",
            "airbnb"
        ]
        
        all_findings = []
        
        for target in targets:
            self.log(f"\n--- HUNTING {target.upper()} ---")
            result = self.scan_github_org(target)
            all_findings.append(result)
            
            # Write appropriate alert level
            if result.get("alert_level") == "HIGH":
                self.write_to_ledger("security_alert", result)
            elif result.get("alert_level") in ["MEDIUM", "LOW"]:
                self.write_to_ledger("github_scan", result)
            else:
                self.write_to_ledger("github_error", result)
                
            self.log(f"Completed hunt for {target}")
            time.sleep(2)  # Rate limiting
            
        # Summary
        high_alerts = sum(1 for f in all_findings if f.get("alert_level") == "HIGH")
        total_repos = sum(f.get("new_repos", 0) for f in all_findings)
        total_secrets = sum(len(f.get("secret_keywords", [])) for f in all_findings)
        
        self.log("="*50)
        self.log(f"HUNT COMPLETE: {len(targets)} orgs scanned")
        self.log(f"Total repositories: {total_repos}")
        self.log(f"Security alerts: {high_alerts}")
        self.log(f"Secret keywords found: {total_secrets}")
        self.log("="*50)

if __name__ == "__main__":
    ghost = GhostCommitAgent()
    ghost.run()