import asyncio
from softnexis_git import AsyncClient, Repository

async def main():
    print("--- STARTING SOFTNEXIS GIT CLIENT DEMO ---")
    
    # Open the connection client
    async with AsyncClient() as client:
        
        # TASK 1: Fetch a single repository from GitHub
        print("\n[Task 1] Fetching data for 'psf/requests'...")
        repo = await client.get("/repos/psf/requests", Repository)
        
        print(f"Success! Repository Found: {repo.full_name}")
        print(f"Stars: {repo.stargazers_count} | Forks: {repo.forks_count}")
        print(f"Owner: {repo.owner.login}")
        
        # TASK 2: Fetch a paginated list of items automatically
        print("\n[Task 2] Fetching list of repositories from 'python' organization...")
        count = 0
        async for org_repo in client.get_paginated("/orgs/python/repos", Repository, per_page=5):
            print(f" -> Found project: {org_repo.name}")
            
            # Stop early after 5 items so our screen doesn't flood with text
            count += 1
            if count >= 5:
                print(" -> Stopping the loop early for demonstration purposes.")
                break
        
        # BONUS: Print remaining hourly API limits allowed by GitHub
        print(f"\n[Status] Remaining GitHub API calls: {client.rate_limit_remaining}")

if __name__ == "__main__":
    # Start the asynchronous runtime engine
    asyncio.run(main())