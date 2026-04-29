
# cli/commands.py
import click
import secrets
import webbrowser
import requests
from .auth_flow import generate_pkce_data  # <--- THIS FIXES THE ERROR
from .callback_server import start_local_server
from .storage import save_credentials, get_tokens
from rich.console import Console
from rich.table import Table


@click.group()
def cli():
    """Insighta Labs+ CLI Tool"""
    pass

@cli.command()
def login():
    """Authenticate via GitHub using PKCE"""
    verifier, challenge = generate_pkce_data() # Now defined via import
    
    # State is required for Stage 3 security
    state = secrets.token_urlsafe(16) 
    
    # URL for your Railway Backend
    backend_auth_url = (
        f"https://your-backend.railway.app/auth/github"
        f"?code_challenge={challenge}&state={state}"
    )
    
    click.echo(f"Opening browser for authentication...")
    webbrowser.open(backend_auth_url)
    
    # Capture code from the local server (localhost:8000)
    code, returned_state = start_local_server()
    
    if returned_state != state:
        click.echo("Error: State mismatch. Security risk detected.")
        return

    # Exchange with Backend
    response = requests.post(
        "https://your-backend.railway.app/auth/github/callback",
        json={
            "code": code,
            "state": state,
            "code_verifier": verifier
        }
    )
    
    if response.status_code == 200:
        save_credentials(response.json())
        click.echo("Login successful!")
    else:
        click.echo(f"Login failed: {response.text}")

console = Console()

@cli.command()
@click.option('--limit', default=10, help='Number of profiles per page')
def list(limit):
    """List profiles in a structured table"""
    tokens = get_tokens() # From your storage logic
    if not tokens:
        console.print("[bold red]Error:[/bold red] Please login first.")
        return

    headers = {
        "X-API-Version": "1", # Required by Backend Middleware
        "Authorization": f"Bearer {tokens['access_token']}"
    }

    # "Feedback during operations" requirement (The Loader)
    with console.status("[bold green]Fetching profiles from Insighta Labs+...") as status:
        response = requests.get(
            "https://your-backend.railway.app/api/profiles/",
            headers=headers,
            params={"limit": limit}
        )

    if response.status_code == 200:
        data = response.json()
        
        # Create a Rich Table
        table = Table(title="Profile Intelligence Report")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Gender", style="green")
        table.add_column("Age", justify="right")
        table.add_column("Country")

        for item in data['data']:
            table.add_row(
                str(item['id'])[:8], # Show short UUID
                item['name'],
                item['gender'],
                str(item['age']),
                item['country_id']
            )

        console.print(table)
        console.print(f"\n[dim]Showing page {data['page']} of {data['total_pages']} ({data['total']} total profiles)[/dim]")
    else:
        console.print(f"[bold red]Failed to fetch profiles:[/bold red] {response.text}")

# cli/commands.py

@cli.command()
@click.argument('query')
def search(query):
    """Search profiles using natural language (e.g., 'males from Nigeria')"""
    tokens = get_tokens()
    if not tokens:
        console.print("[bold red]Error:[/bold red] You must login first.")
        return

    headers = {
        "X-API-Version": "1",
        "Authorization": f"Bearer {tokens['access_token']}"
    }

    with console.status(f"[bold blue]Searching for: '{query}'...") as status:
        try:
            # We use the /api/profiles/ endpoint with the 'q' parameter 
            # established in Stage 2 for natural language
            response = requests.get(
                "https://your-backend.railway.app/api/profiles/",
                headers=headers,
                params={"q": query}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if not data['data']:
                    console.print("[yellow]No profiles found matching that query.[/yellow]")
                    return

                table = Table(title=f"Results for: {query}")
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="magenta")
                table.add_column("Age", justify="right")
                table.add_column("Country")

                for item in data['data']:
                    table.add_row(
                        str(item['id'])[:8],
                        item['name'],
                        str(item['age']),
                        item['country_id']
                    )
                console.print(table)
            else:
                console.print(f"[bold red]Search failed:[/bold red] {response.status_code}")
        
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")

# cli/commands.py

@cli.command()
@click.option('--query', '-q', help='Filter the export using natural language')
def export(query):
    """Export profiles to a timestamped CSV file"""
    tokens = get_tokens()
    headers = {
        "X-API-Version": "1",
        "Authorization": f"Bearer {tokens['access_token']}"
    }
    
    params = {"q": query} if query else {}

    with console.status("[bold green]Generating export...") as status:
        response = requests.get(
            "https://your-backend.railway.app/api/profiles/export",
            headers=headers,
            params=params,
            stream=True # Required for file downloads
        )

    if response.status_code == 200:
        # Extract filename from header (e.g., profiles_20240429.csv)
        content_dispo = response.headers.get('Content-Disposition')
        filename = content_dispo.split('filename=')[-1].strip('"')
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        console.print(f"[bold green]Success![/bold green] Data exported to {filename}")
    else:
        console.print("[bold red]Export failed.[/bold red]")